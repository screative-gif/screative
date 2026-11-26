#!/usr/bin/env python3
"""Ekspor carousel/feed yang sudah APPROVED ke PDF vektor untuk diimpor ke Canva (teks tetap bisa diedit).

Pakai:  python3 konten/brand/visual/canva.py konten/visual/<folder>/spec.json
Hasil:  konten/visual/<folder>/<KODE>_canva.pdf   (1 halaman = 1 slide, 1080x1350 px)

Lalu di Canva: Beranda -> Upload -> pilih PDF itu -> buka -> jadi desain yang bisa diedit
(teks, warna, posisi per elemen). Poppins & Open Sauce Sans ada di pustaka font Canva, jadi font ikut.

Cara kerja: memakai HTML yang sama persis dengan render.py (tampilan identik dengan PNG approved),
tapi dicetak ke PDF, bukan di-screenshot. Foto besar diperkecil dulu (maks 1600 px) supaya PDF ringan.
Butuh: Chrome (sama seperti render.py), Pillow, dan pypdf (`pip install pypdf`) untuk menggabung halaman.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402  (slide_html, CHROME, ROOT)

PAGE_CSS = "<style>@page{size:1080px 1350px;margin:0}html,body{margin:0}</style>"
MAX_PX = 1600


def kecilkan(path, tmp):
    """Salin foto ke tmp dengan sisi terpanjang maks MAX_PX. Kembalikan path baru (atau asli kalau gagal)."""
    try:
        from PIL import Image
    except ImportError:
        return path
    p = path if os.path.isabs(path) else os.path.join(render.ROOT, path)
    if not os.path.exists(p) or not p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        return path
    im = Image.open(p)
    alfa = im.mode in ("RGBA", "LA", "P") and "A" in im.convert("RGBA").getbands() and im.convert("RGBA").getextrema()[3][0] < 255
    # Foto PNG tanpa transparansi (mis. hasil AI) dijadikan JPG supaya PDF muat di Discord (< 9 MB).
    if max(im.size) <= MAX_PX and (alfa or not p.lower().endswith(".png")):
        return path
    im.thumbnail((MAX_PX, MAX_PX))
    out = os.path.join(tmp, f"{len(os.listdir(tmp))}_{os.path.basename(p)}")
    if alfa:
        im.save(out, optimize=True)
    else:
        out = os.path.splitext(out)[0] + ".jpg"
        im.convert("RGB").save(out, quality=88)
    return out


def ganti_foto(obj, tmp):
    """Telusuri slide; setiap string yang menunjuk file gambar di folder visual diganti versi kecil."""
    if isinstance(obj, dict):
        return {k: ganti_foto(v, tmp) for k, v in obj.items()}
    if isinstance(obj, list):
        return [ganti_foto(v, tmp) for v in obj]
    if isinstance(obj, str) and obj.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and "konten/visual/" in obj:
        return kecilkan(obj, tmp)
    return obj


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_path = sys.argv[1]
    spec = render.siapkan_spec(json.load(open(spec_path, encoding="utf-8")))
    od = spec["output_dir"]
    od = od if os.path.isabs(od) else os.path.join(render.ROOT, od)
    kode = os.path.basename(od.rstrip("/")).split("_", 1)[-1]
    tmp = tempfile.mkdtemp()
    fototmp = os.path.join(tmp, "foto")
    os.makedirs(fototmp)
    pdfs = []
    for i, s in enumerate(spec["slides"], 1):
        no = s.get("nomor", i)
        doc = render.slide_html(ganti_foto(s, fototmp), no).replace("</head>", PAGE_CSS + "</head>", 1)
        hp = os.path.join(tmp, f"slide-{no:02d}.html")
        open(hp, "w", encoding="utf-8").write(doc)
        pdf = os.path.join(tmp, f"slide-{no:02d}.pdf")
        subprocess.run([render.CHROME, "--headless=new", *render.CHROME_EXTRA, "--disable-gpu",
                        "--allow-file-access-from-files", f"--user-data-dir={os.path.join(tmp, 'prof')}",
                        "--no-pdf-header-footer", "--virtual-time-budget=3000",
                        f"--print-to-pdf={pdf}", "file://" + hp], check=True, capture_output=True)
        pdfs.append(pdf)
    out = os.path.join(od, f"{kode}_canva.pdf")
    try:
        from pypdf import PdfReader, PdfWriter
        w = PdfWriter()
        for p in pdfs:
            w.add_page(PdfReader(p).pages[0])  # 1 slide = 1 halaman
        w.write(out)
    except ImportError:
        if not shutil.which("pdfunite"):
            sys.exit("Butuh pypdf untuk menggabung halaman: pip install pypdf")
        subprocess.run(["pdfunite", *pdfs, out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("✓", os.path.relpath(out, render.ROOT), f"({len(pdfs)} halaman, {os.path.getsize(out) // 1024} KB)")


if __name__ == "__main__":
    main()
