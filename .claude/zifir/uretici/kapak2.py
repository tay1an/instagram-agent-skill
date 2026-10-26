"""Kapak: sahnenin karesi + ortada şarkı sözü + ZİFİR — UZAK. Kullanım: kapak2.py <reel adı> <çıktı.jpg>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ad, cikti = sys.argv[1], sys.argv[2]
sys.argv = ["x", "/dev/null"]
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import reels as R

W, H = R.W, R.H
_, cls, kw, soz, _, _ = next(r for r in R.REELS if r[0] == ad)
sc = cls(**kw)
f = sc.base.copy(); sc.anim(f, 2.0)
cw, ch = R.BW / 1.03, R.BH / 1.03
x0, y0 = (R.BW - cw) / 2, (R.BH - ch) / 2
M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
fr = cv2.warpAffine(f, M, (W, H))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = np.clip(1.2 - 0.8 * (((xx - W / 2) / (W * .7)) ** 2 + ((yy - H / 2) / (H * .65)) ** 2), 0.3, 1)[..., None]
img = Image.fromarray(np.clip(fr * vign * 0.8, 0, 255).astype(np.uint8)).convert("RGBA")

fnt = ImageFont.truetype(R.F_ITAL, 112); fnt.set_variation_by_axes([500])
d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
satirlar, cur = [], ""
for w in soz.split():
    t = (cur + " " + w).strip()
    if d0.textlength(t, font=fnt) <= 880:
        cur = t
    else:
        satirlar.append(cur); cur = w
satirlar.append(cur)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
lh = 132
# Görselin ana nesnesi ortadaysa (kalp, ay, mum) yazı onun altına ya da üstüne alınır.
merkez = {"03-kalp": 0.66, "05-ufuk": 0.64, "06-alev": 0.27}.get(ad, 0.5) * H
y = merkez - lh * len(satirlar) / 2 + lh / 2 - 30
for s in satirlar:
    d.text((W / 2, y), s, font=fnt, fill=(255, 246, 235, 255), anchor="mm"); y += lh
d.text((W / 2, y + 40), "ZİFİR  —  UZAK", font=ImageFont.truetype(R.F_SANS, 34), fill=(235, 225, 215, 215), anchor="mm")
a = np.asarray(lay)[..., 3].astype(np.float32) / 255
sh = cv2.GaussianBlur(a, (0, 0), 14)
base = np.asarray(img).astype(np.float32)
base[..., :3] *= (1 - np.clip(sh * 1.6, 0, 1) * 0.65)[..., None]
Image.alpha_composite(Image.fromarray(base.astype(np.uint8)), lay).convert("RGB").save(cikti, quality=92)
