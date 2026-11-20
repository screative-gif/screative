#!/usr/bin/env python3
"""Jembatan Discord untuk workflow carousel otomatis Seakun (pilar 2).

Pakai (dari root proyek):
  python3 otomatis/discord.py cek                                  # tes koneksi bot + akses channel (tidak mengirim apa pun)
  python3 otomatis/discord.py kirim-topik <radar-topik.md> [--siklus 2026-11-23]
                                                                    # kirim 10 topik + bobot, pasang reaksi 1️⃣–🔟
  python3 otomatis/discord.py baca-pilihan [--siklus …]            # baca reaksi & balasan tim -> JSON keputusan
  python3 otomatis/discord.py kirim-hasil <folder-visual> [--siklus …] [--revisi N] [--catatan "…"]
                                                                    # kirim slide + caption + PDF Canva, pasang ✅
  python3 otomatis/discord.py baca-feedback [--siklus …]           # baca ✅ & balasan tim setelah hasil terakhir -> JSON
  python3 otomatis/discord.py kirim "<teks>"                        # pesan bebas (status, info topik terpilih, dll.)
  python3 otomatis/discord.py status                                # tampilkan state siklus terakhir

Token bot dibaca dari env DISCORD_BOT_TOKEN. Kalau kosong, skrip tidak mengirim header Authorization
sendiri dan mengandalkan "network secret" environment yang menyisipkan header
`Authorization: Bot <token>` untuk host discord.com. Token tidak pernah dicetak.

State per siklus disimpan di otomatis/state.json (id pesan Discord, topik terpilih, status).
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


def kirim_pesan(teks, reply_to=None, files=None):
    """Kirim teks (dipotong per 2000 karakter). files = [(nama, bytes)]. Return pesan pertama."""
    potongan = _potong(teks, 2000) if teks else [""]
    pertama = None
    for i, bagian in enumerate(potongan):
        payload = {"content": bagian, "allowed_mentions": {"parse": []}}
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
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"siklus": {}}


def simpan_state(st):
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def siklus_aktif(st, nama=None):
    if nama:
        if nama not in st["siklus"]:
            sys.exit(f"Siklus {nama} belum ada di state.json")
        return nama, st["siklus"][nama]
    if not st["siklus"]:
        sys.exit("Belum ada siklus di state.json. Jalankan kirim-topik dulu.")
    nama = sorted(st["siklus"])[-1]
    return nama, st["siklus"][nama]


# ------------------------------------------------------------------ radar topik
def baca_radar(path):
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
        if len(topik) == 10:
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
    topik = baca_radar(a.radar)
    siklus = a.siklus or dt.datetime.now(WIB).strftime("%Y-%m-%d")
    hari = {0: "Senin", 4: "Jumat"}.get(dt.date.fromisoformat(siklus).weekday(), "")
    posting = {0: "Selasa", 4: "Sabtu"}.get(dt.date.fromisoformat(siklus).weekday(), "besok")
    baris = [f"📌 **Radar topik carousel {hari} {siklus}** · untuk posting {posting}",
             "Bobot = skor radar (maks 25). Makin tinggi, makin berpotensi ramai.", ""]
    for i, t in enumerate(topik):
        jenis = f" · _{t['jenis']}_" if t["jenis"] else ""
        baris.append(f"{ANGKA[i]} **{t['judul']}** · bobot **{t['skor']}**{jenis}")
    baris += ["",
              "**Cara pilih (sampai 10.00 WIB):**",
              "• Klik reaksi nomor topik yang kamu mau (boleh lebih dari satu).",
              "• Atau **balas pesan ini** dengan topik lain, misalnya: `usul: Kenapa Indomaret & Alfamart selalu bersebelahan?`",
              "Kalau sampai 10.00 belum ada respon, aku pakai topik dengan bobot tertinggi."]
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
        suara.append({"no": t["no"], "judul": t["judul"], "skor": t["skor"], "suara": len(pemilih),
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
    # Keputusan: usulan eksplisit terbaru > suara terbanyak (seri -> bobot) > bobot tertinggi.
    if usulan:
        keputusan = {"cara": "usulan-tim", "judul": usulan[-1]["teks"], "oleh": usulan[-1]["oleh"]}
    elif any(x["suara"] for x in suara):
        top = max(suara, key=lambda x: (x["suara"], x["skor"]))
        keputusan = {"cara": "suara-tim", "no": top["no"], "judul": top["judul"], "suara": top["suara"]}
    else:
        top = max(topik, key=lambda x: x["skor"])
        keputusan = {"cara": "bobot-tertinggi", "no": top["no"], "judul": top["judul"], "skor": top["skor"]}
    out = {"siklus": nama, "suara": [x for x in suara if x["suara"]], "usulan": usulan,
           "komentar_lain": komentar, "keputusan_otomatis": keputusan,
           "catatan": "Komentar_lain bisa berisi pilihan dalam kata-kata (mis. 'nomor 3 aja'): Naka membaca & memutuskan."}
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
    nama, s = siklus_aktif(st, a.siklus)
    folder = Path(a.folder)
    revisi = a.revisi or 0
    judul = s.get("terpilih", {}).get("judul", folder.name)
    kepala = (f"🎨 **Carousel {nama}{' · revisi ' + str(revisi) if revisi else ''}**\n**{judul}**\n"
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
        "Aku cek respon jam 12.00, 15.00, 18.00, 21.00 WIB, dan besok 08.00 WIB.")
    reaksi(akhir["id"], APPROVE)
    s.setdefault("hasil", []).append({"revisi": revisi, "folder": str(folder), "pesan_awal": pertama["id"],
                                      "pesan_review": akhir["id"], "dikirim": dt.datetime.now(WIB).isoformat(timespec="minutes")})
    s["status"] = "menunggu-review"
    simpan_state(st)
    print(json.dumps({"siklus": nama, "pesan_review": akhir["id"], "jumlah_slide": len(slides)}))


def cmd_baca_feedback(a):
    st = muat_state()
    nama, s = siklus_aktif(st, a.siklus)
    if not s.get("hasil"):
        sys.exit(f"Siklus {nama} belum punya hasil yang dikirim.")
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
    print(json.dumps({"siklus": nama, "revisi_terakhir": h["revisi"], "folder": h["folder"],
                      "approve": approve, "approve_lewat_teks": [f["oleh"] for f in teks_approve],
                      "feedback_baru": [f for f in feedback if f not in teks_approve]}, ensure_ascii=False, indent=1))


def cmd_tandai(a):
    """Catat id pesan feedback yang sudah dikerjakan & ubah status siklus."""
    st = muat_state()
    nama, s = siklus_aktif(st, a.siklus)
    if a.feedback:
        s.setdefault("feedback_diproses", []).extend(x for x in a.feedback.split(",") if x)
    if a.status:
        s["status"] = a.status
    if a.terpilih:
        s["terpilih"] = json.loads(a.terpilih)
    simpan_state(st)
    print(json.dumps({"siklus": nama, "status": s["status"]}, ensure_ascii=False))


def cmd_kirim(a):
    m = kirim_pesan(a.teks, reply_to=a.balas)
    print(json.dumps({"id": m["id"]}))


def cmd_status(a):
    st = muat_state()
    if not st["siklus"]:
        print("Belum ada siklus."); return
    nama, s = siklus_aktif(st, a.siklus)
    print(json.dumps({"siklus": nama, **{k: v for k, v in s.items() if k != "topik"}}, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cek")
    x = sub.add_parser("kirim-topik"); x.add_argument("radar"); x.add_argument("--siklus")
    x = sub.add_parser("baca-pilihan"); x.add_argument("--siklus")
    x = sub.add_parser("kirim-hasil"); x.add_argument("folder"); x.add_argument("--siklus")
    x.add_argument("--revisi", type=int); x.add_argument("--catatan")
    x = sub.add_parser("baca-feedback"); x.add_argument("--siklus")
    x = sub.add_parser("tandai"); x.add_argument("--siklus"); x.add_argument("--feedback", help="id pesan, dipisah koma")
    x.add_argument("--status", help="menunggu-pilihan | produksi | menunggu-review | revisi | approved | gagal")
    x.add_argument("--terpilih", help='JSON, mis. {"judul":"…","cara":"suara-tim","kode":"C-HARBOLNAS"}')
    x = sub.add_parser("kirim"); x.add_argument("teks"); x.add_argument("--balas")
    x = sub.add_parser("status"); x.add_argument("--siklus")
    a = p.parse_args()
    {"cek": cmd_cek, "kirim-topik": cmd_kirim_topik, "baca-pilihan": cmd_baca_pilihan, "kirim-hasil": cmd_kirim_hasil,
     "baca-feedback": cmd_baca_feedback, "tandai": cmd_tandai, "kirim": cmd_kirim, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
