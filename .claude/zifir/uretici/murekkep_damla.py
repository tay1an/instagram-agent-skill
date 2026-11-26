"""Zifir — Uzak: berrak suya lacivert-siyah mürekkep damlaları. Her söz satırında yeni damla düşer,
kıvrılarak açılır (alan bükmeli gürültü + Beer-Lambert emilim). Sözler altta zarif italik.
Kullanım: murekkep_damla.py out.mp4 | murekkep_damla.py x "t1,t2" sheet.jpg
"""
import math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

BURA = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
SES = os.path.join(BURA, "uzak.m4a")
T0, SURE = 58.8, 21.0
NF = int(SURE * FPS)
rng = np.random.default_rng(12)
MW, MH = 270, 480
my_, mx_ = np.mgrid[0:MH, 0:MW].astype(np.float32)

SU_UST = np.array([226, 232, 236], np.float32)   # berrak, hafif soğuk su
SU_ALT = np.array([196, 206, 214], np.float32)
EMIS = np.array([2.9, 2.5, 1.55], np.float32)     # lacivert-siyah mürekkep (kırmızıyı en çok emer)
YAZI_RENK = np.array([16, 20, 32], np.float32)

SATIR = [(59.04, 62.87, "Oysa seni sana\nanlatan ben idim"),
         (62.87, 66.62, "Ben eğer yok isem\nsen de olmazsın dedim"),
         (66.62, 69.73, "Yan yana ağacız\ngölge yeter bize"),
         (69.73, 76.70, "Köklerini\nversene")]
SATIR = [(a - T0, b - T0, m) for a, b, m in SATIR]
# damlalar: (düşme anı, x 0-1, boyut) — ilk damla ilk karede düşmekte
DAMLA = [(0.0, 0.50, 1.0), (3.85, 0.30, 0.8), (7.6, 0.70, 0.85), (10.7, 0.45, 1.1), (14.6, 0.62, 0.7), (17.4, 0.36, 0.75)]

# --- gürültü dokuları (aynalı döşeme: dikişsiz)
OKT = []
for s in (40, 20, 10, 5):
    o = cv2.GaussianBlur(rng.random((1024 // s, 1024 // s)).astype(np.float32), (0, 0), 0.8)
    o = cv2.resize(o, (1024, 1024), interpolation=cv2.INTER_CUBIC)
    OKT.append(((o - o.mean()) / o.std() * 0.28).astype(np.float32))


def fbm(x, y, t, kay=(7.0, -9.0)):
    v = np.zeros_like(x); a = 0.5; tot = 0
    for j, o in enumerate(OKT):
        ox = (x + 300 + t * kay[0] * (j + 1)) % 2044; oy = (y + 200 + t * kay[1] * (j + 1)) % 2044
        ox = np.where(ox < 1022, ox, 2044 - ox); oy = np.where(oy < 1022, oy, 2044 - oy)
        v += a * cv2.remap(o, ox.astype(np.float32), oy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        tot += a; a *= 0.55
    return v / tot


def damla_yogunluk(g, x0, boy, tohum):
    """Düşme anından g sn sonra tek damlanın yoğunluğu: düşen damla → çarpma → mantar gibi açılan bulut + sap."""
    if g < 0:
        return None
    cx = x0 * MW
    vur = 0.28
    if g < vur:   # suya girmeden önce: küçük, uzun damla
        y = -6 + (MH * 0.16 + 6) * (g / vur) ** 2
        return np.exp(-((mx_ - cx) ** 2 + ((my_ - y) / 1.8) ** 2) / (2 * (3.2 * boy) ** 2)) * 5
    q = g - vur
    k = 1 - math.exp(-q / 1.3)
    cy = MH * 0.16 + MH * 0.30 * k * boy           # bulut batar
    R = (10 + 62 * k) * boy
    A = 14 + 40 * min(1, q / 2.5)
    o = tohum * 97.0
    wx = mx_ + A * fbm(mx_ + o, my_, q); wy = my_ + A * fbm(mx_ + 137 + o, my_ + 291, q)
    wx2 = wx + A * 0.55 * fbm(wx * 1.9 + 50 + o, wy * 1.9, q * 1.3); wy2 = wy + A * 0.55 * fbm(wx * 1.9 + o, wy * 1.9 + 80, q * 1.3)
    d = np.sqrt(((wx2 - cx) / R) ** 2 + ((wy2 - cy) / (R * 0.9)) ** 2)
    bas_ = np.clip(1.05 - d, 0, 1) ** 1.3
    # mantar başının altından sarkan ince iplikler ve üstte sap
    sap = np.exp(-((wx2 - cx) / (2.0 + 5 * k)) ** 2) * np.clip((cy - wy2) / 40, 0, 1) * np.clip((wy2 - MH * 0.14) / 20, 0, 1)
    ip = np.exp(-((wx2 - cx - 0.6 * R * np.sin(wy2 * 0.05 + o)) / 3.0) ** 2) * np.clip((wy2 - cy) / (R * 2.2), 0, 1) * (wy2 > cy) * np.exp(-(wy2 - cy) / (R * 0.9)) * (wy2 < cy + R * 2.0)
    f = fbm(wx2 * 2.4 + o, wy2 * 2.4, q * 0.7)
    doku = 0.3 + 1.5 * np.clip(0.5 + f * 1.7, 0, 1) ** 1.5
    seyrel = 1.0 / (1 + q * 0.12)                    # yayıldıkça açılır
    return (bas_ * doku * 1.2 + sap * 0.55 * (1 - k * 0.6) + ip * 0.5) * seyrel


def halka(g, x0):
    """Damla çarpınca yüzeyde açılan ince halka."""
    q = g - 0.28
    if q < 0 or q > 0.9:
        return 0
    r = 6 + 70 * (1 - math.exp(-q / 0.35))
    rr = np.sqrt((mx_ - x0 * MW) ** 2 + ((my_ - MH * 0.16) * 3.2) ** 2)
    return np.exp(-((rr - r) / 1.1) ** 2) * (1 - q / 0.9) * 0.35


# --- yazı
FONT = ImageFont.truetype(os.path.join(BURA, "fonts", "PlayfairDisplay-Italic[wght].ttf"), 84)
try:
    FONT.set_variation_by_name("Medium")
except Exception:
    pass
FK = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf", 28)


def yazi(m, font, ara=1.2):
    sat = m.split("\n"); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    asc, desc = font.getmetrics(); lh = int((asc + desc) * ara)
    gw = int(max(d0.textlength(x, font=font) for x in sat)) + 40
    im = Image.new("L", (gw, lh * len(sat) + 30), 0); d = ImageDraw.Draw(im)
    for i, x in enumerate(sat):
        d.text(((gw - d0.textlength(x, font=font)) / 2, 10 + i * lh), x, font=font, fill=255)
    return np.asarray(im, np.float32) / 255


SOZ = [(a, b, yazi(m, FONT)) for a, b, m in SATIR]
# kapanış: Spotify çağrısı (sakin, slogan değil)
FC = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf", 58)
SON1 = yazi("Şimdi Spotify'da", FC, 1.1)
SON2 = yazi("Zifir — Uzak", FONT)
SON_BAS = 76.85 - T0
KUNYE = yazi("Z İ F İ R   —   U Z A K", FK)


def bas(fr, a, x, y, renk, op):
    h, w = a.shape; x, y = int(x), int(y)
    m = a[..., None] * op
    fr[y:y + h, x:x + w] = fr[y:y + h, x:x + w] * (1 - m) + np.asarray(renk, np.float32) * m


yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
ZEMIN = SU_UST * (1 - yy) + SU_ALT * yy
_, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIN = (1 - 0.35 * np.clip(((xx - W / 2) / (W * 0.8)) ** 2 + ((np.mgrid[0:H, 0:W][0] - H * 0.45) / (H * 0.7)) ** 2, 0, 1))[..., None]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(SURE), "-i", SES, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True).stdout


def kare(f):
    t = f / FPS
    d = np.zeros((MH, MW), np.float32); hal = np.zeros((MH, MW), np.float32)
    for k, (td, x0, boy) in enumerate(DAMLA):
        y = damla_yogunluk(t - td, x0, boy, k + 1)
        if y is not None:
            d += y; hal += halka(t - td, x0)
    # su hafif ışık kırınımı (kostik) ile yaşar
    kost = 0.5 + fbm(mx_ * 1.4, my_ * 1.4, t * 0.6, kay=(3, 2)) * 1.2
    dd = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)[..., None]
    fr = ZEMIN * (0.97 + 0.05 * cv2.resize(kost, (W, H))[..., None]) * np.exp(-dd * EMIS * 0.9)
    fr = fr * (1 - cv2.resize(hal, (W, H))[..., None] * 0.25)
    for a, b, al in SOZ:
        if a - 0.1 <= t < b:
            g = t - a
            op = min(1, (g + 0.1) / 0.6) * min(1, (b - t) / 0.35)
            x = W / 2 - al.shape[1] / 2; y = 1300 - al.shape[0] / 2 + (1 - min(1, (g + 0.1) / 0.6)) ** 2 * 14
            bas(fr, cv2.GaussianBlur(al, (0, 0), 14), x, y + 4, (255, 255, 255), op * 0.5)
            bas(fr, al, x, y, YAZI_RENK, op)
    if t >= SON_BAS:
        g = t - SON_BAS
        o1 = min(1, g / 0.5); o2 = min(1, max(0, g - 0.35) / 0.5)
        for al, y, o in ((SON1, 1230, o1), (SON2, 1320, o2)):
            x = W / 2 - al.shape[1] / 2
            bas(fr, cv2.GaussianBlur(al, (0, 0), 14), x, y + 4, (255, 255, 255), o * 0.5)
            bas(fr, al, x, y + (1 - o) * 12, YAZI_RENK, o)
    else:
        bas(fr, KUNYE, W / 2 - KUNYE.shape[1] / 2, 1500, YAZI_RENK, 0.6)
    fr = fr * VIN
    if t > SURE - 0.4:
        fr = fr * (1 - (t - (SURE - 0.4)) / 0.4 * 0.85)
    fr = fr + rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)
    return np.clip(fr, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    if sys.argv[1] == "x":
        ims = [cv2.resize(kare(int(float(v) * FPS)), (270, 480)) for v in sys.argv[2].split(",")]
        cv2.imwrite(sys.argv[3], cv2.cvtColor(np.concatenate(ims, 1), cv2.COLOR_RGB2BGR)); sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-ss", str(T0), "-t", str(SURE), "-i", SES, "-af", f"afade=t=in:d=0.05,afade=t=out:st={SURE - 1.2}:d=1.2",
                           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "8M", "-maxrate", "11M",
                           "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                           "-shortest", sys.argv[1]], stdin=subprocess.PIPE)
    for f in range(NF):
        ff.stdin.write(kare(f).tobytes())
    ff.stdin.close(); ff.wait(); print("done")
