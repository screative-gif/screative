#!/usr/bin/env python3
"""Posting carousel harian ke Instagram @seakun.id lewat Instagram Graph API (tahap 2 workflow).

Pakai (dari root proyek):
  python3 otomatis/instagram.py cek                       # tes token + kuota posting (tidak memposting apa pun)
  python3 otomatis/instagram.py posting [--hari …] --uji   # siapkan container saja, TIDAK tayang
  python3 otomatis/instagram.py posting [--hari …]         # posting carousel hari itu (default hari ini WIB)

Aturan user 26 Nov 2026: tayang Sabtu, Senin, Kamis 17.00 WIB. Tanpa ✅ sampai 17.00 tetap diposting, asal status
`approved` atau `menunggu-review` (revisi/produksi yang belum selesai = tidak diposting).

Gambar: Instagram mengambil gambar dari URL publik. Skrip memakai URL lampiran slide di pesan hasil
Discord terakhir (revisi yang di-approve), jadi tidak perlu hosting lain. Caption dari caption.txt di folder.

Token: System-user token (tidak kedaluwarsa) disisipkan network secret environment ke host
graph.facebook.com (`Authorization: Bearer …`). Kalau env IG_ACCESS_TOKEN ada, itu yang dipakai.
Token tidak pernah dicetak.

Aman diulang: kalau hari itu sudah punya `posting.media_id` di state.json, skrip berhenti tanpa posting lagi.
"""
import argparse, datetime as dt, json, os, re, sys, time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import discord as dc  # noqa: E402  (jembatan Discord di folder yang sama)

GRAPH = "https://graph.facebook.com/v23.0"
IG_USER = dc.CFG.get("instagram", {}).get("ig_user_id", "17841459636109092")
MAKS_SLIDE = 20  # Graph API menerima carousel > 10 (uji 26 Nov 2026: 11 slide OK)


def _h():
    tok = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def g(method, path, **kw):
    for coba in range(4):
        try:
            r = requests.request(method, GRAPH + path, headers=_h(), timeout=90, **kw)
        except requests.RequestException as e:
            if coba == 3:
                sys.exit(f"Graph API {path} gagal jaringan: {e}")
            time.sleep(5 * (coba + 1)); continue
        if r.status_code >= 500 and coba < 3:
            time.sleep(5 * (coba + 1)); continue
        if r.status_code >= 400:
            sys.exit(f"Graph API {method} {path} gagal {r.status_code}: {r.text[:400]}")
        return r.json()


def tunggu_siap(cid, batas=300):
    t0 = time.time()
    while True:
        s = g("GET", f"/{cid}", params={"fields": "status_code,status"})
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            sys.exit(f"Container {cid} gagal: {s.get('status')}")
        if time.time() - t0 > batas:
            sys.exit(f"Container {cid} belum siap setelah {batas} detik: {s}")
        time.sleep(4)


def cmd_cek(_a):
    akun = g("GET", f"/{IG_USER}", params={"fields": "username,followers_count,media_count"})
    kuota = g("GET", f"/{IG_USER}/content_publishing_limit", params={"fields": "quota_usage,config"})["data"][0]
    print(json.dumps({"akun": akun, "kuota_24jam": f"{kuota['quota_usage']}/{kuota['config']['quota_total']}"},
                     ensure_ascii=False))


def url_slide(hasil):
    """URL lampiran slide-* dari pesan hasil Discord (pesan_awal + lanjutannya sebelum pesan review)."""
    pesan = [dc.api("GET", f"/channels/{dc.CHANNEL}/messages/{hasil['pesan_awal']}", headers=dc._headers())]
    pesan += [m for m in dc.pesan_setelah(hasil["pesan_awal"]) if int(m["id"]) < int(hasil["pesan_review"])]
    lamp = [a for m in pesan if m["author"].get("bot") for a in m.get("attachments", [])
            if re.match(r"slide-\d+\.(png|jpe?g)$", a["filename"])]
    lamp.sort(key=lambda a: a["filename"])
    return [a["url"] for a in lamp]


def cmd_posting(a):
    st = dc.muat_state()
    nama, s = dc.hari_aktif(st, a.hari)
    if s.get("posting", {}).get("media_id"):
        print(json.dumps({"hari": nama, "sudah_tayang": s["posting"]}, ensure_ascii=False)); return
    boleh = ("approved", "menunggu-review")
    if s.get("status") not in boleh and not a.paksa:
        sys.exit(f"Carousel {nama} berstatus '{s.get('status')}', bukan {' / '.join(boleh)}. Tidak diposting.")
    if not s.get("hasil"):
        sys.exit(f"Carousel {nama} belum punya hasil di Discord.")
    hasil = s["hasil"][-1]
    folder = dc.ROOT / hasil["folder"]
    status_txt = folder / "STATUS.txt"
    tanpa_approve = s.get("status") != "approved"
    caption = (folder / "caption.txt").read_text(encoding="utf-8").strip()
    urls = url_slide(hasil)
    if not 2 <= len(urls) <= MAKS_SLIDE:
        sys.exit(f"Jumlah slide {len(urls)} di luar batas carousel (2–{MAKS_SLIDE}).")

    anak = []
    for u in urls:
        anak.append(g("POST", f"/{IG_USER}/media", data={"image_url": u, "is_carousel_item": "true"})["id"])
    for cid in anak:
        tunggu_siap(cid)
    induk = g("POST", f"/{IG_USER}/media",
              data={"media_type": "CAROUSEL", "children": ",".join(anak), "caption": caption})["id"]
    tunggu_siap(induk)
    if a.uji:
        print(json.dumps({"hari": nama, "uji": True, "slide": len(anak), "container": induk,
                          "catatan": "Container siap tapi TIDAK dipublikasikan (kedaluwarsa sendiri dalam 24 jam)."},
                         ensure_ascii=False)); return

    media = g("POST", f"/{IG_USER}/media_publish", data={"creation_id": induk})["id"]
    link = g("GET", f"/{media}", params={"fields": "permalink"}).get("permalink", "")
    waktu = dt.datetime.now(dc.WIB).isoformat(timespec="minutes")
    s["posting"] = {"media_id": media, "permalink": link, "waktu": waktu, "slide": len(anak),
                    "tanpa_approve": tanpa_approve}
    s["status"] = "tayang"
    dc.simpan_state(st)
    lama = status_txt.read_text().rstrip("\n") + "\n" if status_txt.exists() else ""
    status_txt.write_text(lama + f"TAYANG {waktu} {link}{' (tanpa approve)' if tanpa_approve else ''}\n")
    print(json.dumps({"hari": nama, "tanpa_approve": tanpa_approve, "media_id": media, "permalink": link}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cek")
    x = sub.add_parser("posting"); x.add_argument("--hari", help="tanggal posting YYYY-MM-DD, default hari ini WIB")
    x.add_argument("--uji", action="store_true", help="siapkan container tanpa mempublikasikan")
    x.add_argument("--paksa", action="store_true", help="abaikan cek status (hanya atas perintah user)")
    a = p.parse_args()
    {"cek": cmd_cek, "posting": cmd_posting}[a.cmd](a)


if __name__ == "__main__":
    main()
