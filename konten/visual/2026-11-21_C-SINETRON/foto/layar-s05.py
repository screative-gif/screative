# Isi layar TV putih di s05.jpg dengan potongan buram gambar layar TV dari cover.jpg -> s05-layar.jpg
from PIL import Image, ImageFilter, ImageDraw
import numpy as np
F = 'konten/visual/2026-11-21_C-SINETRON/foto/'
im = Image.open(F + 's05.jpg').convert('RGB')
x0, y0, x1, y1 = 1900, 280, 4170, 1640
src = Image.open(F + 'cover.jpg').convert('RGB').crop((4450, 480, 6900, 1800))
cont = src.resize((x1 - x0, y1 - y0)).filter(ImageFilter.GaussianBlur(14))
layer = Image.new('RGB', im.size); layer.paste(cont, (x0, y0))
a = np.asarray(im).astype(int)
m = a.min(axis=2) > 215
box = np.zeros_like(m); box[y0:y1, x0:x1] = True
mask = Image.fromarray(((m & box) * 255).astype('uint8')).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
Image.composite(layer, im, mask).save(F + 's05-layar.jpg', quality=92)
