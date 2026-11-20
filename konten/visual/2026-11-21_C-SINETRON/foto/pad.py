from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import sys
im = Image.open('konten/visual/2026-11-21_C-SINETRON/foto/cover-layar.jpg')
p = int(sys.argv[1]); x0 = int(sys.argv[2])
H = 4080 + p; W = int(H * 0.8)
c = im.crop((x0, 0, x0 + W, 4080))
fill = ImageOps.flip(c.crop((0, 0, W, p))).filter(ImageFilter.GaussianBlur(60))
fill = ImageEnhance.Brightness(fill).enhance(0.55)
canvas = Image.new('RGB', (W, H)); canvas.paste(fill, (0, 0)); canvas.paste(c, (0, p))
# blend seam
band = 300
top = canvas.crop((0, p - band, W, p + band)).filter(ImageFilter.GaussianBlur(40))
mask = Image.linear_gradient('L').resize((W, 2 * band))
mask = Image.eval(mask, lambda v: 255 - abs(v - 128) * 2)
canvas.paste(top, (0, p - band), mask)
canvas.resize((1080, 1350), Image.LANCZOS).save('konten/visual/2026-11-21_C-SINETRON/foto/cover-crop.jpg', quality=92)
