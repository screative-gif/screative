# Isi layar CRT polos di s03-ai.png dengan potongan buram layar TV dari cover.jpg + vignette CRT,
# lalu samarkan badge bezel & label panel kontrol palsu hasil AI -> s03-ai-layar.png
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import numpy as np
F = 'konten/visual/2026-11-21_C-SINETRON/foto/'
im = Image.open(F + 's03-ai.png').convert('RGB')
x0, y0, x1, y1 = 696, 690, 1278, 1124
w, h = x1 - x0, y1 - y0
src = Image.open(F + 'cover.jpg').convert('RGB').crop((4700, 480, 6700, 1800))
cont = src.resize((w, h)).filter(ImageFilter.GaussianBlur(8))
# vignette CRT: tepi gelap, sedikit kebiruan
yy, xx = np.mgrid[0:h, 0:w]
d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
v = np.clip(1.0 - 0.55 * np.clip(d - 0.55, 0, None) ** 1.4, 0.35, 1.0)
c = np.asarray(cont).astype(float) * v[..., None]
c[..., 2] = np.clip(c[..., 2] * 1.06 + 6, 0, 255)
cont = Image.fromarray(c.astype('uint8'))
# garis scan tipis
sl = Image.new('L', (w, h), 255); dr = ImageDraw.Draw(sl)
for y in range(0, h, 4): dr.line([(0, y), (w, y)], fill=232)
cont = Image.composite(cont, Image.new('RGB', (w, h)), sl)
layer = im.copy(); layer.paste(cont, (x0, y0))
# mask: layar terang di dalam kotak bersudut bulat (ikut lengkung)
a = np.asarray(im).astype(int)
bright = a.min(axis=2) > 110
rr = Image.new('L', im.size, 0); ImageDraw.Draw(rr).rounded_rectangle((x0 + 4, y0 + 2, x1 - 4, y1 - 4), radius=60, fill=255)
m = bright & (np.asarray(rr) > 0)
mask = Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))
mask = ImageChops.multiply(mask, rr.filter(ImageFilter.GaussianBlur(6)))
out = Image.composite(layer, im, mask)
# samarkan badge bezel bawah & label panel kontrol kanan
for box, r in [((630, 1095, 700, 1150), 8), ((900, 1118, 1080, 1160), 10), ((1300, 680, 1420, 1150), 7)]:
    reg = out.crop(box).filter(ImageFilter.GaussianBlur(r))
    out.paste(reg, box[:2])
out.save(F + 's03-ai-layar.png')
