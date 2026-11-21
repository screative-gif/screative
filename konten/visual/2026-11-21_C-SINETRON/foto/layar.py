from PIL import Image, ImageFilter, ImageEnhance, ImageChops
import numpy as np, sys
src = 'konten/visual/2026-11-21_C-SINETRON/foto/cover.jpg'
im = Image.open(src).convert('RGB')
# isi layar: potongan vertikal dari gambar di layar TV yang sama (konten sama di TV & HP)
cont = im.crop((4950, 420, 5650, 1850)).filter(ImageFilter.GaussianBlur(6))
cont = ImageEnhance.Brightness(cont).enhance(1.05)
W, H = im.size
quad = (2190, 1974, 2058, 3576, 2838, 3576, 2925, 1974)  # TL, BL, BR, TR (PIL QUAD: ul, ll, lr, ur) - map dest->src needs inverse
# bangun gambar konten di posisi tujuan dengan perspektif: pakai transform PERSPECTIVE
def coeffs(pa, pb):
    A = []
    for (x, y), (X, Y) in zip(pa, pb):
        A.append([x, y, 1, 0, 0, 0, -X*x, -X*y]); A.append([0, 0, 0, x, y, 1, -Y*x, -Y*y])
    A = np.array(A, float); B = np.array(pb, float).reshape(8)
    return np.linalg.solve(A, B).tolist()
dst = [(2190, 1974), (2925, 1974), (2838, 3576), (2058, 3576)]
cw, ch = cont.size
srcpts = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
c = coeffs(dst, srcpts)
warped = cont.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)
a = np.asarray(im).astype(int)
mask = (a.min(axis=2) > 185)
from PIL import ImageDraw
rg = Image.new('L', (W, H), 0); ImageDraw.Draw(rg).polygon([(2196,1980),(2919,1980),(2832,3570),(2064,3570)], fill=255)
reg = np.asarray(rg) > 0
mask = Image.fromarray(((mask & reg) * 255).astype('uint8')).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2))
out = Image.composite(warped, im, mask)
out.save('konten/visual/2026-11-21_C-SINETRON/foto/cover-layar.jpg', quality=92)
x0 = int(sys.argv[1]) if len(sys.argv) > 1 else 1450
out.crop((x0, 0, x0 + 3264, 4080)).resize((1080, 1350), Image.LANCZOS).save('konten/visual/2026-11-21_C-SINETRON/foto/cover-crop.jpg', quality=92)
