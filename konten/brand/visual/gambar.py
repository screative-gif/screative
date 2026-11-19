#!/usr/bin/env python3
"""Ambil gambar untuk slide secara otomatis: foto stok & AI (Magnific), foto faktual (Wikimedia Commons).

Pakai (dari root proyek):
  python3 konten/brand/visual/gambar.py stok  "<kata kunci>" <folder> [--nama x] [--pilih 1]   # cari foto stok Magnific, unduh hasil ke-N
  python3 konten/brand/visual/gambar.py cari  "<kata kunci>"                                    # lihat 8 kandidat stok (id + judul + preview) tanpa mengunduh
  python3 konten/brand/visual/gambar.py unduh <id> <folder> [--nama x]                           # unduh foto stok Magnific berdasarkan id
  python3 konten/brand/visual/gambar.py ai    "<prompt bahasa Inggris>" <folder> [--nama x] [--rasio social_post_4_5|widescreen_16_9|square_1_1]
  python3 konten/brand/visual/gambar.py wiki  "<kata kunci>" <folder> [--nama x] [--pilih 1]    # foto Wikimedia Commons + catat kredit

Setiap unduhan dicatat di <folder>/SUMBER.md (asal, id/URL, lisensi/kredit) — wajib untuk audit lisensi.
Key Magnific dikirim otomatis oleh proxy environment (header x-magnific-api-key); jangan menaruh key di file.
Catatan biaya: unduh stok & generate AI memakai kredit API Magnific user. Pakai `cari` dulu, unduh seperlunya.
Kalau unduhan gagal dengan "CONNECT tunnel failed 403", host CDN-nya belum diizinkan di environment: laporkan host-nya ke Naka.
"""
import argparse, datetime, json, os, re, sys, time, urllib.parse, urllib.request

API = "https://api.magnific.com/v1"
HDR = {"x-magnific-api-key": os.environ.get("MAGNIFIC_API_KEY", "proxy-injected"), "Accept-Language": "id-ID"}
UA = "screative-content-research/1.0 (personal, non-commercial tooling)"


def req(url, data=None, headers=None, timeout=60):
    h = dict(headers or {})
    h.setdefault("User-Agent", UA)
    body = json.dumps(data).encode() if data is not None else None
    if body:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method="POST" if body else "GET")
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.read()


def jget(url, **kw):
    return json.loads(req(url, headers=HDR, **kw))


def simpan(url, folder, nama, ext_default=".jpg"):
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ext_default
    path = os.path.join(folder, f"{nama}{ext}")
    open(path, "wb").write(req(url, timeout=120))
    return path


def catat(folder, baris):
    p = os.path.join(folder, "SUMBER.md")
    baru = not os.path.exists(p)
    with open(p, "a") as f:
        if baru:
            f.write("# Sumber gambar\n\n| File | Asal | Detail | Lisensi / kredit | Tanggal |\n|---|---|---|---|---|\n")
        f.write("| " + " | ".join(baris + [datetime.date.today().isoformat()]) + " |\n")


def cari(term, n=8):
    q = urllib.parse.urlencode({"term": term, "limit": n, "filters[content_type][photo]": 1})
    return jget(f"{API}/resources?{q}").get("data", [])


def unduh(rid, folder, nama):
    d = jget(f"{API}/resources/{rid}/download")["data"]
    path = simpan(d["url"], folder, nama)
    catat(folder, [os.path.basename(path), "Magnific stok", f"id {rid}", f"lisensi Magnific (https://www.magnific.com/profile/license/pdf/{rid})"])
    return path


def ai(prompt, folder, nama, rasio):
    t = json.loads(req(f"{API}/ai/mystic", {"prompt": prompt, "aspect_ratio": rasio, "resolution": "2k"}, HDR))["data"]["task_id"]
    for _ in range(60):
        time.sleep(5)
        d = jget(f"{API}/ai/mystic/{t}")["data"]
        if d["status"] == "COMPLETED":
            path = simpan(d["generated"][0], folder, nama, ".png")
            catat(folder, [os.path.basename(path), "Magnific AI (Mystic)", f"task {t}; prompt: {prompt[:120].replace('|', '/')}", "hasil AI milik user"])
            return path
        if d["status"] == "FAILED":
            sys.exit(f"AI gagal: {d}")
    sys.exit("AI timeout")


def wiki(term, folder, nama, pilih):
    q = urllib.parse.urlencode({"action": "query", "generator": "search", "gsrsearch": f"filetype:bitmap {term}", "gsrnamespace": 6,
                                "gsrlimit": 10, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 2000, "format": "json"})
    pages = sorted(json.loads(req(f"https://commons.wikimedia.org/w/api.php?{q}")).get("query", {}).get("pages", {}).values(),
                   key=lambda p: p.get("index", 99))
    if not pages:
        sys.exit("Tidak ada hasil Wikimedia.")
    for i, p in enumerate(pages[:8], 1):
        print(f"{i}. {p['title']}")
    p = pages[pilih - 1]
    ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    clean = lambda k: re.sub("<[^>]+>", "", m.get(k, {}).get("value", "")).strip()
    path = simpan(ii.get("thumburl") or ii["url"], folder, nama)
    kredit = f"{clean('Artist') or 'Tidak diketahui'} / Wikimedia Commons, {clean('LicenseShortName')}"
    catat(folder, [os.path.basename(path), "Wikimedia Commons", p["title"].replace("|", "/"), kredit])
    print("Kredit (tulis di sumber slide):", kredit)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stok", "cari", "unduh", "ai", "wiki"])
    ap.add_argument("isi")
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--nama", default=None)
    ap.add_argument("--pilih", type=int, default=1)
    ap.add_argument("--rasio", default="social_post_4_5")
    a = ap.parse_args()
    nama = a.nama or re.sub(r"[^a-z0-9]+", "-", a.isi.lower())[:40].strip("-")
    if a.mode == "cari":
        for r in cari(a.isi):
            print(r["id"], "|", r.get("title"), "|", (r.get("image") or {}).get("source", {}).get("url", ""))
        return
    if not a.folder:
        sys.exit("folder tujuan wajib diisi")
    if a.mode == "stok":
        hasil = cari(a.isi)
        if not hasil:
            sys.exit("Tidak ada hasil stok.")
        r = hasil[a.pilih - 1]
        print("dipilih:", r["id"], r.get("title"))
        print("✓", unduh(r["id"], a.folder, nama))
    elif a.mode == "unduh":
        print("✓", unduh(a.isi, a.folder, nama))
    elif a.mode == "ai":
        print("✓", ai(a.isi, a.folder, nama, a.rasio))
    else:
        print("✓", wiki(a.isi, a.folder, nama, a.pilih))


if __name__ == "__main__":
    main()
