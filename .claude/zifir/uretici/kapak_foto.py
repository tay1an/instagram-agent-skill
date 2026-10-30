"""Fotoğraftan kapak: dikey kırp, sözü ve künyeyi ekle.
Kullanım: kapak_foto.py <foto> <çıktı.jpg> <söz; "" ise yazısız> <merkez_x 0-1> <yazı_y 0-1> <açık|koyu|filtre adı>
                       [yakınlaştırma] [merkez_y 0-1] [künye] [yazı boyu]"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
foto, cikti, soz, mx, ty, ton = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
W, H = 1080, 1920
im = Image.open(foto).convert("RGB")
w, h = im.size
# İsteğe bağlı: yakınlaştırma ve dikey merkez (figür kenarda kalıyorsa).
zoom = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
my = float(sys.argv[8]) if len(sys.argv) > 8 else 0.5
cw = min(w, round(h * W / H)); ch = round(cw * H / W)
cw, ch = round(cw / zoom), round(ch / zoom)
x0 = int(min(max(mx * w - cw / 2, 0), w - cw)); y0 = int(min(max(my * h - ch / 2, 0), h - ch))
im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
# Videonun sahnesine göre ton: (gölge rengi, ışık rengi, parlaklık). Split-toning + kontrast.
FILTRE = {
    "kalp":  ((8, 1, 4), (230, 80, 90), 0.42),
    "yagmur": ((6, 10, 26), (170, 200, 255), 0.60),
    "sicak-yagmur": ((20, 8, 14), (255, 170, 120), 0.60),
    "agac":  ((22, 12, 34), (255, 175, 110), 0.72),
    "gece":  ((4, 8, 22), (190, 205, 255), 0.55),
    "mum":   ((16, 8, 4), (255, 190, 120), 0.62),
    "gunbatimi": ((24, 12, 36), (255, 170, 110), 0.72),
    "lila":  ((14, 12, 36), (255, 200, 190), 0.68),
}
if ton in FILTRE:
    g, i, k = FILTRE[ton]
    L = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255
    L = np.clip((L - 0.5) * 1.3 + 0.5, 0, 1) ** (1.15 + (0.6 - k))  # kontrast; koyu sahnelerde gölgeler daha derin
    a = (np.array(g, np.float32) * (1 - L) + np.array(i, np.float32) * L) * (0.35 + 0.65 * k)
    a = a * 0.8 + np.asarray(im).astype(np.float32) * 0.2 * k  # dokuyu korumak için az miktar orijinal
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= np.clip(1.25 - 0.85 * (((xx - W / 2) / (W * .7)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2), 0.25, 1)[..., None]
    # Üstteki açık gökyüzünü videodaki koyu arka plana yaklaştır (yazı orada durur).
    a *= np.clip(0.38 + (yy / H) / 0.55 * 0.62, 0.38, 1)[..., None]
else:
    a = a * 0.96 + 4                                         # hafif soluk film tonu
a += np.random.default_rng(0).normal(0, 6, a.shape[:2])[..., None]
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
if not soz.strip():  # yazısız kapak (29 Ekim'den sonra reel kapakları): yalnızca fotoğraf
    im.save(cikti, quality=92)
    sys.exit(0)
renk = (28, 26, 26) if ton == "koyu" else (255, 246, 235)
KUNYE = sys.argv[9] if len(sys.argv) > 9 else "ZİFİR  —  UZAK"
BOY = int(sys.argv[10]) if len(sys.argv) > 10 else 104
fnt = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PlayfairDisplay-Italic[wght].ttf"), BOY); fnt.set_variation_by_axes([500])
d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
sat, cur = [], ""
for k in soz.split():
    t = (cur + " " + k).strip()
    if d0.textlength(t, font=fnt) <= 880: cur = t
    else: sat.append(cur); cur = k
sat.append(cur)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
lh = round(BOY * 1.19); y = ty * H - lh * len(sat) / 2 + lh / 2
for s in sat:
    d.text((W / 2, y), s, font=fnt, fill=renk + (255,), anchor="mm"); y += lh
d.text((W / 2, y + 36), KUNYE, font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 32), fill=renk + (215,), anchor="mm")
if ton != "koyu":  # açık yazıya yumuşak gölge
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh.point(lambda v: int(v * 0.6)))
Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB").save(cikti, quality=92)
