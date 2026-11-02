"""4:5 carousel kareleri: fotoğraf + filtre + büyük yazı. Kullanım: carousel.py <çıktı klasörü>"""
import os, sys
ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["/dev/null"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402
import foto_video as FV  # noqa: E402

W, H = 1080, 1350
D = os.path.dirname(os.path.abspath(__file__))
SERIF = os.path.join(D, "fonts", "PlayfairDisplay-Italic[wght].ttf")
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
S = "stok/"
# (foto, filtre, mx, zoom, my, üst küçük yazı, büyük yazı, alt yazı, yazı merkezi y)
KARELER = [
    (S + "07-sahil.jpg", "gunbatimi", 0.5, 1.0, 0.45, "", "Bugün duyman gereken iki şey var.", "kaydır  →", 0.24),
    (S + "03-eller.jpg", "lila", 0.5, 1.0, 0.5, "BİR", "Sen çok değerlisin.", "Bunu sana kimse söylemediyse, şimdi duydun.", 0.22),
    (S + "02-sehir.jpg", "mum", 0.5, 1.0, 0.5, "İKİ", "Bunu sana bir şarkıyla söyledim.", "ZİFİR  —  UZAK", 0.2),
    (S + "09-lamba.jpg", "dogal", 0.5, 1.0, 0.5, "", "Oysa seni sana\nanlatan ben idim.", "— Uzak", 0.7),
    (S + "05-iskele.jpg", "yagmur", 0.46, 1.6, 0.45, "", "Uzak şimdi Spotify'da.", "Kulaklığını tak, sonuna kadar dinle.\nLink profilde.", 0.22),
]


def font(yol, boy, agirlik=None):
    f = ImageFont.truetype(yol, boy)
    if agirlik:
        f.set_variation_by_axes([agirlik])
    return f


def sar(metin, fnt, gen):
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    out = []
    for par in metin.split("\n"):
        cur = ""
        for k in par.split():
            t = (cur + " " + k).strip()
            if d0.textlength(t, font=fnt) <= gen:
                cur = t
            else:
                out.append(cur); cur = k
        out.append(cur)
    return out


def kare(foto, ton, mx, zoom, my, ust, buyuk, alt, ty, cikti):
    FV.W, FV.H = W, H
    a = FV.hazirla(foto, ton, mx, zoom, my)
    bh, bw = a.shape[:2]
    y0, x0 = (bh - H) // 2, (bw - W) // 2
    a = a[y0:y0 + H, x0:x0 + W]
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    a = a * np.clip(0.55 + 1.6 * np.abs(yy - ty), 0.55, 1)[..., None]  # yazının arkasını koyulaştır
    a += np.random.default_rng(0).normal(0, 5, a.shape[:2])[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fb, fu, fa = font(SERIF, 92, 500), font(SANS, 30), font(SANS, 34)
    sat = sar(buyuk, fb, 900); lh = 112
    blok = len(sat) * lh + (70 if ust else 0) + (90 if alt else 0)
    y = ty * H - blok / 2
    renk = (255, 246, 235)
    if ust:
        d.text((W / 2, y + 15), ust, font=fu, fill=renk + (200,), anchor="mm"); y += 70
    for s in sat:
        d.text((W / 2, y + lh / 2), s, font=fb, fill=renk + (255,), anchor="mm"); y += lh
    if alt:
        y += 30
        for s in alt.split("\n"):
            d.text((W / 2, y + 22), s, font=fa, fill=renk + (215,), anchor="mm"); y += 48
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(16))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh.point(lambda v: int(v * 0.55)))
    Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB").save(cikti, quality=93)


if __name__ == "__main__":
    for i, k in enumerate(KARELER, 1):
        kare(*k, os.path.join(ARGS[0], f"{i}.jpg"))
    print("done")
