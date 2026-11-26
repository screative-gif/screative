#!/usr/bin/env python3
"""Jembatan Discord untuk workflow carousel otomatis Seakun (pilar 2).

Jadwal (keputusan user 26 Nov 2026, menggantikan jadwal harian 21 Nov): carousel tayang SABTU, SENIN, KAMIS 17.00 WIB.
Radar topik Senin & Jumat; suara tim radar Senin -> Senin + Kamis (2 topik), radar Jumat -> Sabtu (1 topik).

Pakai (dari root proyek):
  python3 otomatis/discord.py cek                                  # tes koneksi bot + akses channel (tidak mengirim apa pun)
  python3 otomatis/discord.py kirim-topik <radar-topik.md> [--siklus 2026-11-23]
                                                                    # kirim 10 topik + bobot, pasang reaksi 1️⃣–🔟
  python3 otomatis/discord.py baca-pilihan [--siklus …]            # baca reaksi & balasan tim -> JSON + usulan plot harian
  python3 otomatis/discord.py plot [--siklus …] [--pilihan JSON]   # simpan topik per hari tayang (2 atau 1) ke state
  python3 otomatis/discord.py kirim-hasil <folder-visual> [--hari …] [--revisi N] [--catatan "…"]
                                                                    # kirim slide + caption + PDF Canva, pasang ✅
  python3 otomatis/discord.py baca-feedback [--hari …]             # baca ✅ & balasan tim setelah hasil terakhir -> JSON
  python3 otomatis/discord.py baca-balasan <id-pesan>              # pesan tim (yang boleh) setelah id-pesan -> JSON
  python3 otomatis/discord.py tandai [--hari …] [--status …] [--terpilih JSON] [--feedback ids]
  python3 otomatis/discord.py kirim "<teks>" [--balas <id>] [--sebut-grup Growth]  # pesan bebas
  python3 otomatis/discord.py status [--hari …]                     # state hari ini + siklus radar yang berlaku

`--hari` = tanggal posting (YYYY-MM-DD), default hari ini WIB. `--siklus` = tanggal radar (Senin/Jumat).

Token bot dibaca dari env DISCORD_BOT_TOKEN. Kalau kosong, skrip tidak mengirim header Authorization
sendiri dan mengandalkan "network secret" environment yang menyisipkan header
`Authorization: Bot <token>` untuk host discord.com. Token tidak pernah dicetak.

State di otomatis/state.json: "siklus" (per radar: topik, pesan_topik, plot) dan "harian"
(per tanggal posting: terpilih, status, hasil, feedback_diproses, posting).
Hanya user di config.json "user_boleh_respon" yang dihitung; respon orang lain diabaikan.
"""
import argparse, datetime as dt, io, json, os, re, sys, time, urllib.parse
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("Butuh paket requests: pip install requests")

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "otomatis"
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
STATE_PATH = HERE / "state.json"
API = "https://discord.com/api/v10"
CHANNEL = CFG["discord"]["channel_id"]
BOLEH = set(CFG["discord"]["user_boleh_respon"])
WIB = dt.timezone(dt.timedelta(hours=7))
ANGKA = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
APPROVE = "✅"
BATAS_UNGGAH = 9 * 1024 * 1024  # batas aman per pesan (limit Discord untuk server biasa 10 MB)


# ------------------------------------------------------------------ HTTP
def _headers(json_body=True):
    h = {"User-Agent": "DiscordBot (https://github.com/screative-gif/screative, 1.0)"}
    tok = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if tok:
        h["Authorization"] = f"Bot {tok}"
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def api(method, path, **kw):
    url = API + path
    for _ in range(5):
        r = requests.request(method, url, timeout=60, **kw)
        if r.status_code == 429:  # rate limit
            time.sleep(float(r.json().get("retry_after", 1)) + 0.2)
            continue
        if r.status_code >= 400:
            pesan = r.text[:300]
            if r.status_code == 401:
                pesan += "\n→ Token bot belum terpasang/salah. Lihat otomatis/README.md bagian 'Token bot'."
            if r.status_code == 403:
                pesan += "\n→ Bot belum punya izin di channel ini (View Channel, Send Messages, Attach Files, Add Reactions, Read Message History)."
            sys.exit(f"Discord {method} {path} gagal {r.status_code}: {pesan}")
        return r.json() if r.content else None
    sys.exit("Discord terus membalas rate limit, coba lagi nanti.")


def kirim_pesan(teks, reply_to=None, files=None, roles=None):
    """Kirim teks (dipotong per 2000 karakter). files = [(nama, bytes)]. roles = id role yang boleh di-mention. Return pesan pertama."""
    potongan = _potong(teks, 2000) if teks else [""]
    pertama = None
    for i, bagian in enumerate(potongan):
        payload = {"content": bagian, "allowed_mentions": {"parse": [], "roles": list(roles or [])}}
        if reply_to and i == 0:
            payload["message_reference"] = {"message_id": reply_to, "fail_if_not_exists": False}
        if files and i == len(potongan) - 1:
            payload["attachments"] = [{"id": n, "filename": f[0]} for n, f in enumerate(files)]
            multipart = [("payload_json", (None, json.dumps(payload), "application/json"))]
            for n, (nama, data) in enumerate(files):
                multipart.append((f"files[{n}]", (nama, data)))
            m = api("POST", f"/channels/{CHANNEL}/messages", headers=_headers(False), files=multipart)
        else:
            m = api("POST", f"/channels/{CHANNEL}/messages", headers=_headers(), json=payload)
        pertama = pertama or m
    return pertama


def _potong(teks, n):
    out, buf = [], ""
    for baris in teks.split("\n"):
        if len(buf) + len(baris) + 1 > n:
            out.append(buf.rstrip("\n"))
            buf = ""
        buf += baris + "\n"
    if buf.strip():
        out.append(buf.rstrip("\n"))
    return out


def reaksi(msg_id, emoji):
    api("PUT", f"/channels/{CHANNEL}/messages/{msg_id}/reactions/{urllib.parse.quote(emoji)}/@me", headers=_headers())
    time.sleep(0.35)


def siapa_reaksi(msg_id, emoji):
    users = api("GET", f"/channels/{CHANNEL}/messages/{msg_id}/reactions/{urllib.parse.quote(emoji)}?limit=100",
                headers=_headers()) or []
    return [u for u in users if u["id"] in BOLEH]


def pesan_setelah(msg_id):
    """Semua pesan setelah msg_id (urut lama -> baru)."""
    out, after = [], msg_id
    while True:
        batch = api("GET", f"/channels/{CHANNEL}/messages?after={after}&limit=100", headers=_headers()) or []
        if not batch:
            break
        batch.sort(key=lambda m: int(m["id"]))
        out += batch
        after = batch[-1]["id"]
        if len(batch) < 100:
            break
    return out


def waktu_wib(msg):
    return dt.datetime.fromisoformat(msg["timestamp"]).astimezone(WIB).strftime("%a %d %b %H.%M WIB")


# ------------------------------------------------------------------ state
def muat_state():
    st = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    st.setdefault("siklus", {})
    st.setdefault("harian", {})
    return st


def simpan_state(st):
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def hari_ini():
    return dt.datetime.now(WIB).strftime("%Y-%m-%d")


def siklus_aktif(st, nama=None):
    """Siklus radar: yang diminta, atau radar terbaru yang tanggalnya <= hari ini."""
    if nama:
        if nama not in st["siklus"]:
            sys.exit(f"Siklus {nama} belum ada di state.json")
        return nama, st["siklus"][nama]
    calon = [k for k in st["siklus"] if k <= hari_ini()] or list(st["siklus"])
    if not calon:
        sys.exit("Belum ada siklus di state.json. Jalankan kirim-topik dulu.")
    nama = sorted(calon)[-1]
    return nama, st["siklus"][nama]


def hari_aktif(st, tanggal=None, buat=False):
    """Data carousel untuk satu tanggal posting (default hari ini WIB)."""
    tanggal = tanggal or hari_ini()
    if tanggal not in st["harian"]:
        if not buat:
            sys.exit(f"Belum ada carousel untuk {tanggal} di state.json (jalankan plot / tandai --terpilih dulu).")
        st["harian"][tanggal] = {"status": "belum-produksi"}
    return tanggal, st["harian"][tanggal]


NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
HARI_TAYANG = (0, 3, 5)   # Senin, Kamis, Sabtu (keputusan user 26 Nov 2026)
HARI_RADAR = (0, 4)       # Senin, Jumat
LABEL_TAYANG = "Sabtu, Senin & Kamis 17.00 WIB"


def hari_tayang(tanggal):
    return dt.date.fromisoformat(tanggal).weekday() in HARI_TAYANG


def jangkauan(siklus):
    """Tanggal tayang yang dilayani radar ini: dari tanggal radar sampai sebelum radar berikutnya, hanya hari tayang.
    Senin -> Senin + Kamis, Jumat -> Sabtu."""
    d0 = dt.date.fromisoformat(siklus)
    out, n = [], 0
    while True:
        d = d0 + dt.timedelta(days=n)
        if n and d.weekday() in HARI_RADAR:
            break
        if d.weekday() in HARI_TAYANG:
            out.append(d.isoformat())
        n += 1
    return out


def label_hari(tanggal):
    d = dt.date.fromisoformat(tanggal)
    return f"{NAMA_HARI[d.weekday()]} {d.day}/{d.month}"


# ------------------------------------------------------------------ radar topik
def baca_radar(path, maks=10):
    """Ambil 10 baris pertama tabel radar: nomor, judul (teks tebal pertama), skor, pemicu."""
    topik = []
    for baris in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|(.+?)\|\s*\**\s*(\d+)\s*\**[^|]*\|([^|]*)\|", baris)
        if not m:
            continue
        sel = m.group(2)
        judul = re.search(r"\*\*(.+?)\*\*", sel)
        judul = (judul.group(1) if judul else sel).strip()
        jenis = re.search(r"·\s*([^|·]+)$", sel.strip())
        topik.append({"no": int(m.group(1)), "judul": judul, "skor": int(m.group(3)),
                      "jenis": jenis.group(1).strip() if jenis else "", "pemicu": m.group(4).strip()})
        if len(topik) == maks:
            break
    if not topik:
        sys.exit(f"Tidak menemukan tabel topik di {path}")
    return topik


# ------------------------------------------------------------------ perintah
def cmd_cek(a):
    me = api("GET", "/users/@me", headers=_headers())
    ch = api("GET", f"/channels/{CHANNEL}", headers=_headers())
    print(json.dumps({"bot": me.get("username"), "bot_id": me.get("id"), "channel": ch.get("name"),
                      "guild_id": ch.get("guild_id"), "ok": True}, ensure_ascii=False))


def cmd_kirim_topik(a):
    lewati = {int(x) for x in (a.lewati or "").split(",") if x.strip()}
    topik = [t for t in baca_radar(a.radar, 10 + len(lewati)) if t["no"] not in lewati][:10]
    siklus = a.siklus or hari_ini()
    hari = jangkauan(siklus)
    # Radar Jumat: tidak ada produksi Jumat, suara dikumpulkan sampai produksi Sabtu 10.00.
    batas = a.batas if not hari or hari[0] == siklus else f"{label_hari(hari[0])} {a.batas}"
    baris = [f"📌 **Radar topik carousel {label_hari(siklus)}** · untuk posting {label_hari(hari[0])} – {label_hari(hari[-1])} ({len(hari)} carousel, tayang {LABEL_TAYANG})",
             "Bobot = skor radar (maks 25). Makin tinggi, makin berpotensi ramai.", ""]
    for i, t in enumerate(topik):
        jenis = f" · _{t['jenis']}_" if t["jenis"] else ""
        baris.append(f"{ANGKA[i]} **{t['judul']}** · bobot **{t['skor']}**{jenis}")
    baris += ["",
              f"**Cara pilih (sampai {batas} WIB):**",
              f"• Klik reaksi nomor topik yang kamu mau (boleh lebih dari satu). **{len(hari)} topik dengan suara terbanyak** jadi carousel {' & '.join(label_hari(h) for h in hari)}.",
              "• Atau **balas pesan ini** dengan topik lain, misalnya: `usul: Kenapa Indomaret & Alfamart selalu bersebelahan?`",
              f"Kalau suaranya kurang, sisanya aku isi dengan topik berbobot tertinggi. Jadwalnya aku kirim {batas} WIB."]
    m = kirim_pesan("\n".join(baris))
    for i in range(len(topik)):
        reaksi(m["id"], ANGKA[i])
    st = muat_state()
    st["siklus"][siklus] = {"radar": str(a.radar), "topik": topik, "pesan_topik": m["id"],
                            "status": "menunggu-pilihan", "dikirim": dt.datetime.now(WIB).isoformat(timespec="minutes")}
    simpan_state(st)
    print(json.dumps({"siklus": siklus, "pesan_topik": m["id"], "jumlah_topik": len(topik)}))


def cmd_baca_pilihan(a):
    st = muat_state()
    nama, s = siklus_aktif(st, a.siklus)
    topik = s["topik"]
    suara = []
    for i, t in enumerate(topik):
        pemilih = siapa_reaksi(s["pesan_topik"], ANGKA[i])
        suara.append({"emoji": ANGKA[i], "urut": i + 1, "no": t["no"], "judul": t["judul"], "skor": t["skor"], "suara": len(pemilih),
                      "pemilih": [u.get("global_name") or u["username"] for u in pemilih]})
    usulan, komentar = [], []
    for m in pesan_setelah(s["pesan_topik"]):
        if m["author"]["id"] not in BOLEH:
            continue
        teks = m.get("content", "").strip()
        ref = (m.get("message_reference") or {}).get("message_id")
        item = {"oleh": m["author"].get("global_name") or m["author"]["username"], "teks": teks,
                "waktu": waktu_wib(m), "id": m["id"]}
        if re.match(r"(?i)^\s*usul\s*[:\-]", teks):
            item["teks"] = re.sub(r"(?i)^\s*usul\s*[:\-]\s*", "", teks)
            usulan.append(item)
        elif ref == s["pesan_topik"] or teks:
            komentar.append(item)
    out = {"siklus": nama, "suara": [x for x in suara if x["suara"]], "usulan": usulan,
           "komentar_lain": komentar, "plot_otomatis": usul_plot(nama, topik, suara, usulan),
           "catatan": ("plot_otomatis = usulan tim (terbaru dulu) > suara terbanyak (seri -> bobot) > bobot tertinggi, "
                       "satu topik per hari. Komentar_lain bisa berisi pilihan dalam kata-kata (mis. 'nomor 3 aja'): "
                       "Naka membaca, menyesuaikan, lalu menyimpan dengan `plot --pilihan`. Urutan hari tidak penting.")}
    print(json.dumps(out, ensure_ascii=False, indent=1))


def usul_plot(nama, topik, suara, usulan):
    hari = jangkauan(nama)
    pilih = [{"cara": "usulan-tim", "judul": u["teks"], "oleh": u["oleh"]} for u in reversed(usulan)]
    sudah = set()
    for x in sorted([x for x in suara if x["suara"]], key=lambda x: (-x["suara"], -x["skor"])):
        pilih.append({"cara": "suara-tim", "no": x["no"], "judul": x["judul"], "suara": x["suara"], "oleh": ", ".join(x["pemilih"])})
        sudah.add(x["no"])
    for t_ in sorted(topik, key=lambda x: -x["skor"]):
        if t_["no"] not in sudah:
            pilih.append({"cara": "bobot-tertinggi", "no": t_["no"], "judul": t_["judul"], "skor": t_["skor"]})
    return [dict(p, tanggal=h) for h, p in zip(hari, pilih)]


def cmd_plot(a):
    """Simpan topik per tanggal posting. Tanpa --pilihan: pakai plot_otomatis dari baca-pilihan."""
    st = muat_state()
    nama, s = siklus_aktif(st, a.siklus)
    if a.pilihan:
        plot = json.loads(a.pilihan)
    else:
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_baca_pilihan(argparse.Namespace(siklus=nama))
        plot = json.loads(buf.getvalue())["plot_otomatis"]
    hari = jangkauan(nama)
    for i, p in enumerate(plot):
        p.setdefault("tanggal", hari[i] if i < len(hari) else None)
    s["plot"] = {p["tanggal"]: {k: v for k, v in p.items() if k != "tanggal"} for p in plot if p.get("tanggal")}
    s["status"] = "terplot"
    for tgl, p in s["plot"].items():
        h = st["harian"].setdefault(tgl, {"status": "belum-produksi"})
        if h.get("status") in (None, "belum-produksi"):
            h["siklus"] = nama
            h["terpilih"] = dict(p)
    if a.kirim:
        alasan = {"usulan-tim": "usulan {oleh}", "suara-tim": "suara tim", "bobot-tertinggi": "bobot tertinggi"}
        baris = [f"🗓️ **Jadwal carousel {label_hari(min(s['plot']))} – {label_hari(max(s['plot']))}** (tayang {LABEL_TAYANG})", ""]
        for tgl, p in sorted(s["plot"].items()):
            ket = alasan.get(p.get("cara"), p.get("cara", "")).format(oleh=p.get("oleh", "tim"))
            urut = next((ANGKA[i] + " " for i, x in enumerate(s["topik"]) if x["no"] == p.get("no")), "")
            baris.append(f"• **{label_hari(tgl)}** · {urut}{p['judul']} _({ket})_")
        baris += ["", "Mau tukar topik suatu hari? **Balas pesan ini**: `ganti Rabu: <topik lain / nomor emoji di daftar topik>`."]
        s["pesan_jadwal"] = kirim_pesan("\n".join(baris))["id"]
    simpan_state(st)
    print(json.dumps({"siklus": nama, "plot": s["plot"], "pesan_jadwal": s.get("pesan_jadwal")}, ensure_ascii=False, indent=1))


def cmd_baca_balasan(a):
    sudah = set(muat_state().get("balasan_diproses", []))
    out = []
    for m in pesan_setelah(a.pesan):
        if m["author"]["id"] not in BOLEH or m["id"] in sudah:
            continue
        out.append({"id": m["id"], "oleh": m["author"].get("global_name") or m["author"]["username"],
                    "teks": m.get("content", "").strip(), "lampiran": [x["url"] for x in m.get("attachments", [])],
                    "balas_ke": (m.get("message_reference") or {}).get("message_id"), "waktu": waktu_wib(m)})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def _berkas_slide(folder):
    """Slide PNG -> list (nama, bytes); kompres ke JPG kalau total melewati batas unggah."""
    slides = sorted(Path(folder).glob("slide-*.png"))
    if not slides:
        sys.exit(f"Tidak ada slide-*.png di {folder}")
    files = [(p.name, p.read_bytes()) for p in slides]
    if sum(len(b) for _, b in files) > BATAS_UNGGAH:
        from PIL import Image
        files = []
        for p in slides:
            buf = io.BytesIO()
            Image.open(p).convert("RGB").save(buf, "JPEG", quality=88, optimize=True)
            files.append((p.stem + ".jpg", buf.getvalue()))
    return files


def cmd_kirim_hasil(a):
    st = muat_state()
    nama, s = hari_aktif(st, a.hari, buat=True)
    folder = Path(a.folder)
    revisi = a.revisi or 0
    judul = s.get("terpilih", {}).get("judul", folder.name)
    kepala = (f"🎨 **Carousel {label_hari(nama)} (tayang 17.00 WIB){' · revisi ' + str(revisi) if revisi else ''}**\n**{judul}**\n"
              + (f"{a.catatan}\n" if a.catatan else ""))
    slides = _berkas_slide(folder)
    # Slide: maks 10 lampiran per pesan, dibagi kalau ukuran melewati batas.
    kelompok, buf, ukuran = [], [], 0
    for f in slides:
        if buf and (len(buf) == 10 or ukuran + len(f[1]) > BATAS_UNGGAH):
            kelompok.append(buf); buf, ukuran = [], 0
        buf.append(f); ukuran += len(f[1])
    kelompok.append(buf)
    pertama = None
    for i, g in enumerate(kelompok):
        m = kirim_pesan(kepala if i == 0 else f"(lanjutan slide {i + 1}/{len(kelompok)})", files=g)
        pertama = pertama or m
    cap = folder / "caption.txt"
    if cap.exists():
        kirim_pesan("✍️ **Caption:**\n" + cap.read_text(encoding="utf-8").strip())
    pdf = sorted(folder.glob("*_canva.pdf"))
    if pdf and pdf[0].stat().st_size <= BATAS_UNGGAH:
        kirim_pesan("🧩 **Versi Canva (editable):** unduh PDF ini, lalu di Canva pilih *Upload* → PDF jadi desain yang bisa diedit.",
                    files=[(pdf[0].name, pdf[0].read_bytes())])
    elif pdf:
        kirim_pesan(f"🧩 PDF Canva ({pdf[0].stat().st_size // 1048576} MB) terlalu besar untuk Discord; ada di repo: `{pdf[0].relative_to(ROOT)}`")
    akhir = kirim_pesan(
        "**Review dong 🙏**\n"
        f"• Sudah oke → klik {APPROVE} di pesan ini.\n"
        "• Ada revisi → **balas pesan ini** dengan poin-poinnya (sebut nomor slide, mis. `slide 3: angkanya pakai data 2025`).\n"
        f"Aku cek respon jam 12.00, 15.00, dan 16.50 WIB. **Tayang otomatis {label_hari(nama)} 17.00 WIB**, "
        "walaupun belum ada ✅ (keputusan tim). Mau ganti topik hari ini? Balas `ganti topik: …`.")
    reaksi(akhir["id"], APPROVE)
    s.setdefault("hasil", []).append({"revisi": revisi, "folder": str(folder), "pesan_awal": pertama["id"],
                                      "pesan_review": akhir["id"], "dikirim": dt.datetime.now(WIB).isoformat(timespec="minutes")})
    s["status"] = "menunggu-review"
    simpan_state(st)
    print(json.dumps({"hari": nama, "pesan_review": akhir["id"], "jumlah_slide": len(slides)}))


def cmd_baca_feedback(a):
    st = muat_state()
    nama, s = hari_aktif(st, a.hari)
    if not s.get("hasil"):
        sys.exit(f"Carousel {nama} belum punya hasil yang dikirim.")
    h = s["hasil"][-1]
    approve = [u.get("global_name") or u["username"] for u in siapa_reaksi(h["pesan_review"], APPROVE)]
    sudah = set(s.get("feedback_diproses", []))
    feedback = []
    for m in pesan_setelah(h["pesan_awal"]):
        if m["author"]["id"] not in BOLEH or m["id"] in sudah:
            continue
        teks = m.get("content", "").strip()
        lamp = [x["url"] for x in m.get("attachments", [])]
        if teks or lamp:
            feedback.append({"id": m["id"], "oleh": m["author"].get("global_name") or m["author"]["username"],
                             "teks": teks, "lampiran": lamp, "waktu": waktu_wib(m)})
    teks_approve = [f for f in feedback if re.fullmatch(r"(?i)\s*(approve[d]?|acc|oke+|ok|setuju|gas+|✅)\s*[.!]*\s*", f["teks"])]
    print(json.dumps({"hari": nama, "revisi_terakhir": h["revisi"], "folder": h["folder"],
                      "approve": approve, "approve_lewat_teks": [f["oleh"] for f in teks_approve],
                      "feedback_baru": [f for f in feedback if f not in teks_approve]}, ensure_ascii=False, indent=1))


def cmd_tandai(a):
    """Ubah status/topik carousel satu hari & catat id pesan yang sudah dikerjakan."""
    st = muat_state()
    nama, s = hari_aktif(st, a.hari, buat=True)
    if a.feedback:
        s.setdefault("feedback_diproses", []).extend(x for x in a.feedback.split(",") if x)
    if a.balasan:
        st.setdefault("balasan_diproses", []).extend(x for x in a.balasan.split(",") if x)
    if a.status:
        s["status"] = a.status
    if a.terpilih:
        s["terpilih"] = {**s.get("terpilih", {}), **json.loads(a.terpilih)}
    simpan_state(st)
    print(json.dumps({"hari": nama, "status": s["status"], "terpilih": s.get("terpilih")}, ensure_ascii=False))


def cmd_kirim(a):
    roles = []
    if a.sebut_grup:
        rid = CFG["discord"].get("role_grup", {}).get(a.sebut_grup)
        if not rid:
            sys.exit(f"Grup '{a.sebut_grup}' tidak ada di config.json discord.role_grup")
        tanda = f"@{a.sebut_grup}"
        a.teks = a.teks.replace(tanda, f"<@&{rid}>") if tanda in a.teks else f"<@&{rid}> " + a.teks
        roles = [rid]
    m = kirim_pesan(a.teks, reply_to=a.balas, roles=roles)
    print(json.dumps({"id": m["id"]}))


def cmd_status(a):
    st = muat_state()
    tgl = a.hari or hari_ini()
    out = {"hari": tgl, "hari_tayang": hari_tayang(tgl), "carousel": st["harian"].get(tgl)}
    if st["siklus"]:
        nama, s = siklus_aktif(st)
        out["siklus_radar"] = {"siklus": nama, **{k: v for k, v in s.items() if k != "topik"}}
    print(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cek")
    x = sub.add_parser("kirim-topik"); x.add_argument("radar"); x.add_argument("--siklus")
    x.add_argument("--lewati", help="nomor topik radar yang sudah dipakai, dipisah koma")
    x.add_argument("--batas", default="10.00", help="jam batas pilih (WIB), default 10.00")
    x = sub.add_parser("baca-pilihan"); x.add_argument("--siklus")
    x = sub.add_parser("plot"); x.add_argument("--siklus")
    x.add_argument("--kirim", action="store_true", help="kirim jadwal ke Discord & simpan pesan_jadwal")
    x.add_argument("--pilihan", help='JSON list, mis. [{"tanggal":"2026-11-23","judul":"…","cara":"suara-tim","no":3}, …]')
    x = sub.add_parser("baca-balasan"); x.add_argument("pesan")
    x = sub.add_parser("kirim-hasil"); x.add_argument("folder"); x.add_argument("--hari")
    x.add_argument("--revisi", type=int); x.add_argument("--catatan")
    x = sub.add_parser("baca-feedback"); x.add_argument("--hari")
    x = sub.add_parser("tandai"); x.add_argument("--hari"); x.add_argument("--feedback", help="id pesan, dipisah koma")
    x.add_argument("--balasan", help="id pesan balasan (baca-balasan) yang sudah dikerjakan, dipisah koma")
    x.add_argument("--status", help="belum-produksi | produksi | menunggu-review | revisi | approved | tayang | gagal")
    x.add_argument("--terpilih", help='JSON, mis. {"judul":"…","cara":"suara-tim","kode":"C-HARBOLNAS"}')
    x = sub.add_parser("kirim"); x.add_argument("teks"); x.add_argument("--balas")
    x.add_argument("--sebut-grup", help="nama grup di config.json discord.role_grup, mis. Growth (tulisan @Growth di teks diganti mention; kalau tidak ada, mention ditaruh di awal)")
    x = sub.add_parser("status"); x.add_argument("--hari")
    a = p.parse_args()
    {"cek": cmd_cek, "kirim-topik": cmd_kirim_topik, "baca-pilihan": cmd_baca_pilihan, "plot": cmd_plot,
     "baca-balasan": cmd_baca_balasan, "kirim-hasil": cmd_kirim_hasil,
     "baca-feedback": cmd_baca_feedback, "tandai": cmd_tandai, "kirim": cmd_kirim, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
