#!/usr/bin/env python3
"""Sapa: soft selling lewat komentar di postingan Threads orang lain (keputusan user 28 Nov 2026).

Alur (detail di otomatis/SAPA.md):
  1. cari         → Apify mencari postingan Threads yang relate (keyword di otomatis/sapa.json),
                    disaring (umur, penjual/kompetitor, sudah pernah diproses), disimpan sebagai kandidat.
  2. (agent Sapa) → menulis draft komentar per kandidat ke file JSON.
  3. kirim-draft  → tiap draft dikirim ke Discord; tim memberi ✅ (kirim), ❌ (lewati),
                    atau membalas pesan itu dengan teks pengganti.
  4. proses       → draft yang di-✅ dikirim sebagai balasan lewat Threads API dari @diarydheanas.

Pakai (dari root proyek):
  python3 otomatis/sapa.py cek                     # tes token Threads (tidak mengirim apa pun)
  python3 otomatis/sapa.py cari                    # ± $0,1–0,2 Apify; cetak kandidat (JSON)
  python3 otomatis/sapa.py kirim-draft draft.json  # [{post_id, draft, alasan}] → Discord
  python3 otomatis/sapa.py proses [--uji]          # kirim yang di-approve; --uji = buat container saja, tidak tayang
  python3 otomatis/sapa.py status

Token Threads disisipkan network secret ke host graph.threads.net (env THREADS_ACCESS_TOKEN kalau ada).
Token tidak pernah dicetak. Komentar TIDAK PERNAH dikirim tanpa ✅ dari anggota tim di Discord.
"""
import argparse, datetime as dt, json, os, sys, time, urllib.parse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discord as dc  # noqa: E402

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "sapa.json").read_text(encoding="utf-8"))
STATE_PATH = HERE / "sapa_state.json"
THREADS = "https://graph.threads.net/v1.0"
APIFY = "https://api.apify.com/v2"
WIB = dc.WIB


# ------------------------------------------------------------------ state
def muat():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"posts": {}}


def simpan(st):
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def sekarang():
    return dt.datetime.now(WIB)


# ------------------------------------------------------------------ Threads API
def _th_headers():
    tok = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def th(method, path, **kw):
    r = requests.request(method, THREADS + path, headers=_th_headers(), timeout=60, **kw)
    if r.status_code >= 400:
        raise RuntimeError(f"Threads {method} {path} gagal {r.status_code}: {r.text[:300]}")
    return r.json()


def cmd_cek(_a):
    try:
        me = th("GET", "/me", params={"fields": "id,username"})
    except RuntimeError as e:
        sys.exit(f"{e}\n→ Token Threads di network secret graph.threads.net belum benar. Lihat otomatis/SAPA.md bagian Setup.")
    print(json.dumps({"akun": "@" + me.get("username", "?"), "id": me.get("id")}, ensure_ascii=False))


def balas(post_id, teks, uji=False):
    """Buat container balasan; publish kalau bukan uji. Return id post balasan (atau container saat uji)."""
    c = th("POST", "/me/threads", data={"media_type": "TEXT", "text": teks, "reply_to_id": post_id})
    if uji:
        return c["id"]
    time.sleep(5)  # Meta menyarankan jeda sebelum publish
    p = th("POST", "/me/threads_publish", data={"creation_id": c["id"]})
    return p["id"]


# ------------------------------------------------------------------ cari (Apify)
KATA_ID = set("yang ga gak nggak enggak aku gue gw ada mau banget dong sih aja kak buat bisa udah sudah lagi kalau kalo atau tapi juga ini itu dan di ke dari pada sama siapa gimana kenapa".split())


def bahasa_id(teks):
    kata = {w.strip(".,!?\"'()").lower() for w in teks.split()}
    return len(kata & KATA_ID) >= 2


def cmd_cari(a):
    ap, f = CFG["apify"], CFG["filter"]
    inp = {"keywords": CFG["keywords"], "maxPerSource": ap["per_keyword"],
           "maxResults": ap["per_keyword"] * len(CFG["keywords"]), "excludeReplies": True}
    qs = urllib.parse.urlencode({"maxTotalChargeUsd": ap["max_usd_per_run"], "timeout": 280})
    tok = os.environ.get("APIFY_TOKEN", "").strip()
    r = requests.post(f"{APIFY}/acts/{ap['actor'].replace('/', '~')}/run-sync-get-dataset-items?{qs}", json=inp,
                      headers={"Authorization": f"Bearer {tok}"} if tok else {}, timeout=320)
    if r.status_code >= 400:
        sys.exit(f"Apify gagal {r.status_code}: {r.text[:300]}")
    items = r.json()

    st = muat()
    batas = sekarang() - dt.timedelta(days=f["maks_umur_hari"])
    penjual = [k.lower() for k in f["lewati_kata_penjual"]]
    lewati_akun = {u.lower().lstrip("@") for u in f["lewati_akun"]}
    out, alasan_buang = [], {}

    def buang(k):
        alasan_buang[k] = alasan_buang.get(k, 0) + 1

    seen = set()
    for x in items:
        pid, teks, user = str(x.get("postId") or ""), (x.get("text") or "").strip(), (x.get("username") or "").lower()
        if not pid or pid in seen:
            continue
        seen.add(pid)
        if pid in st["posts"]:
            buang("sudah pernah"); continue
        if x.get("isReply"):
            buang("balasan"); continue
        if user in lewati_akun:
            buang("akun sendiri"); continue
        if len(teks) < f["min_teks"]:
            buang("teks pendek"); continue
        if f.get("hanya_indonesia") and not bahasa_id(teks):
            buang("bukan bahasa Indonesia"); continue
        if any(k in teks.lower() for k in penjual):
            buang("penjual/kompetitor"); continue
        try:
            waktu = dt.datetime.fromisoformat(x["publishedAt"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            buang("tanpa tanggal"); continue
        if waktu < batas:
            buang("terlalu lama"); continue
        out.append({"post_id": pid, "url": x.get("postUrl"), "username": x.get("username"), "teks": teks,
                     "waktu": waktu.astimezone(WIB).strftime("%d %b %H.%M WIB"), "keyword": x.get("sourceQuery"),
                     "balasan": x.get("replyCount", 0), "suka": x.get("likeCount", 0)})

    out.sort(key=lambda k: (k["balasan"] + k["suka"]), reverse=True)
    out = out[:CFG["maks_kandidat_per_run"]]
    for k in out:
        st["posts"][k["post_id"]] = {**k, "status": "kandidat", "dicari": sekarang().isoformat(timespec="minutes")}
    simpan(st)
    print(json.dumps({"total_apify": len(items), "dibuang": alasan_buang, "kandidat": out}, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ Discord
def cmd_kirim_draft(a):
    drafts = json.loads(Path(a.file).read_text(encoding="utf-8"))
    st = muat()
    terkirim = 0
    for d in drafts:
        p = st["posts"].get(str(d["post_id"]))
        if not p or p["status"] != "kandidat":
            print(f"lewati {d['post_id']}: bukan kandidat aktif", file=sys.stderr); continue
        if not d.get("draft"):
            p["status"] = "dilewati-agent"; p["alasan"] = d.get("alasan", ""); continue
        teks = (f"💬 **Sapa · draft komentar Threads** ({CFG['akun']})\n"
                f"Post @{p['username']} · {p['waktu']} · {p['url']}\n"
                f"> {p['teks'][:400].replace(chr(10), chr(10) + '> ')}\n\n"
                f"**Draft:**\n{d['draft']}\n\n"
                f"_Kenapa: {d.get('alasan', '-')}_\n"
                f"✅ kirim · ❌ lewati · atau balas pesan ini dengan teks pengganti (diawali `ganti:`)")
        m = dc.kirim_pesan(teks)
        dc.reaksi(m["id"], "✅"); dc.reaksi(m["id"], "❌")
        p.update(status="menunggu", draft=d["draft"], alasan=d.get("alasan", ""), discord_id=m["id"])
        terkirim += 1
    simpan(st)
    print(f"{terkirim} draft terkirim ke Discord.")


def _teks_pengganti(msg_id):
    for m in dc.pesan_setelah(msg_id):
        ref = (m.get("message_reference") or {}).get("message_id")
        isi = (m.get("content") or "").strip()
        if ref == msg_id and m["author"]["id"] in dc.BOLEH and isi.lower().startswith("ganti:"):
            return isi.split(":", 1)[1].strip()
    return None


def cmd_proses(a):
    st = muat()
    hari = sekarang().date().isoformat()
    kuota = CFG["maks_kirim_per_hari"] - sum(1 for p in st["posts"].values()
                                             if p.get("status") == "terkirim" and p.get("dikirim", "")[:10] == hari)
    hasil = []
    for pid, p in st["posts"].items():
        if p["status"] != "menunggu":
            continue
        if dc.siapa_reaksi(p["discord_id"], "❌"):
            p["status"] = "ditolak"; hasil.append((pid, "ditolak")); continue
        oke = dc.siapa_reaksi(p["discord_id"], "✅")
        if not oke:
            continue
        if kuota <= 0:
            hasil.append((pid, "tertunda: kuota harian habis")); continue
        teks = _teks_pengganti(p["discord_id"]) or p["draft"]
        try:
            rid = balas(pid, teks, uji=a.uji)
        except RuntimeError as e:
            p["error"] = str(e)[:300]; hasil.append((pid, f"gagal: {e}")); continue
        if a.uji:
            hasil.append((pid, f"uji OK, container {rid} (tidak tayang)")); continue
        p.update(status="terkirim", teks_terkirim=teks, reply_id=rid, approve_oleh=oke[0].get("username"),
                 dikirim=sekarang().isoformat(timespec="minutes"))
        dc.kirim_pesan(f"✅ Terkirim ke @{p['username']}.", reply_to=p["discord_id"])
        kuota -= 1
        hasil.append((pid, "terkirim"))
        time.sleep(CFG["jeda_kirim_detik"])
    simpan(st)
    print(json.dumps(hasil, ensure_ascii=False, indent=1))


def cmd_status(_a):
    st = muat()
    hitung = {}
    for p in st["posts"].values():
        hitung[p["status"]] = hitung.get(p["status"], 0) + 1
    print(json.dumps(hitung, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cek").set_defaults(f=cmd_cek)
    sub.add_parser("cari").set_defaults(f=cmd_cari)
    k = sub.add_parser("kirim-draft"); k.add_argument("file"); k.set_defaults(f=cmd_kirim_draft)
    p = sub.add_parser("proses"); p.add_argument("--uji", action="store_true"); p.set_defaults(f=cmd_proses)
    sub.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
