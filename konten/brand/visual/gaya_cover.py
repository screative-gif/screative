#!/usr/bin/env python3
"""Gilir gaya cover carousel Fakta Unik (aturan user 26 Nov 2026: cover jangan monoton).

Pakai:  python3 konten/brand/visual/gaya_cover.py            -> gaya cover berikutnya + arahan foto
        python3 konten/brand/visual/gaya_cover.py --riwayat  -> gaya cover tiap carousel sejauh ini

Urutan giliran: lingkar -> editorial -> poster -> lingkar ... (3 gaya tipografi yang disetujui user
19 Nov 2026, lihat konten/brand/visual.md). Gaya berikutnya = gaya sesudah cover carousel TERAKHIR
(folder konten/visual/<tanggal>_C-* terbaru selain folder yang sedang dikerjakan, --kecuali <folder>).
Foto cover (ElevenLabs) dibuat SESUDAH gaya dipilih, dengan komposisi sesuai arahan di bawah.
"""
import glob, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
URUTAN = ["lingkar", "editorial", "poster"]
ARAHAN = {
    "lingkar": ("judul di sepertiga ATAS", "subjek utama di tengah-bawah; ± 45% bagian atas foto tenang/kosong (langit, dinding, latar gelap)"),
    "editorial": ("judul di sepertiga BAWAH", "subjek utama di atas-tengah; ± 45% bagian bawah foto tenang/kosong (meja, lantai, latar gelap)"),
    "poster": ("judul rata kiri, huruf condensed besar", "subjek utama di sisi KANAN; ± 50% sisi kiri foto tenang/kosong"),
}


def riwayat(kecuali=None):
    out = []
    for sp in sorted(glob.glob(os.path.join(ROOT, "konten/visual/*_C-*/spec.json"))):
        folder = os.path.relpath(os.path.dirname(sp), ROOT)
        if kecuali and os.path.normpath(folder) == os.path.normpath(kecuali):
            continue
        try:
            c = json.load(open(sp, encoding="utf-8"))["slides"][0]
        except Exception:
            continue
        if c.get("layout") == "berita":
            out.append((folder, c.get("kartu", "kaca")))
    return out


def berikutnya(kecuali=None):
    r = riwayat(kecuali)
    terakhir = next((g for _, g in reversed(r) if g in URUTAN), None)
    return URUTAN[(URUTAN.index(terakhir) + 1) % len(URUTAN)] if terakhir else URUTAN[0], r


def main():
    kecuali = sys.argv[sys.argv.index("--kecuali") + 1] if "--kecuali" in sys.argv else None
    g, r = berikutnya(kecuali)
    if "--riwayat" in sys.argv:
        for f, k in r:
            print(f"{f}: {k}")
        return
    teks, foto = ARAHAN[g]
    print(f"Gaya cover berikutnya: {g}  (terakhir: {r[-1][1] if r else '-'} di {r[-1][0] if r else '-'})")
    print(f"  Teks : {teks}")
    print(f"  Foto : {foto}")
    print(f'  Spec : slide 1 "layout": "berita", "kartu": "{g}"')


if __name__ == "__main__":
    main()
