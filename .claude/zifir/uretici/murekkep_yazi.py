"""Zifir — Uzak: sözler mürekkeple suya yazılır. Her satırda bir damla düşer; çarptığı noktadan yayılan
mürekkep harfleri oluşturur, satır bitince harfler suda dağılıp bulut olur ve çöker. Kapanış da mürekkeple.
murekkep_damla.py'nin su/damla/gürültü motorunu kullanır.
Kullanım: murekkep_yazi.py out.mp4 | murekkep_yazi.py x "t1,t2" sheet.jpg
"""
import importlib.util, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

BURA = os.path.dirname(os.path.abspath(__file__))
_a = sys.argv; sys.argv = ["x", "none"]
_s = importlib.util.spec_from_file_location("md", os.path.join(BURA, "murekkep_damla.py"))
D = importlib.util.module_from_spec(_s); _s.loader.exec_module(D)
sys.argv = _a
W, H, FPS = D.W, D.H, D.FPS
T0, SURE = D.T0, 21.0
NF = int(SURE * FPS)
MW, MH, mx_, my_ = D.MW, D.MH, D.mx_, D.my_

SATIR = [(59.04, 62.87, "Oysa seni sana\nanlatan ben idim"),
         (62.87, 66.62, "Ben eğer yok isem\nsen de olmazsın dedim"),
         (66.62, 69.73, "Yan yana ağacız\ngölge yeter bize"),
         (69.73, 76.85, "Köklerini\nversene"),
         (76.85, 79.80, "Şimdi Spotify'da\nZifir — Uzak")]
SATIR = [(a - T0, b - T0, m) for a, b, m in SATIR]

FONT = ImageFont.truetype(os.path.join(BURA, "fonts", "PlayfairDisplay-Italic[wght].ttf"), 128)
try:
    FONT.set_variation_by_name("Bold")
except Exception:
    pass
YAZI_Y = 900   # harflerin dikey merkezi
CARPMA_Y = YAZI_Y - 40


def maske(m):
    sat = m.split("\n"); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    asc, desc = FONT.getmetrics(); lh = int((asc + desc) * 1.12)
    gw = int(max(d0.textlength(x, font=FONT) for x in sat)) + 40; gh = lh * len(sat) + 30
    im = Image.new("L", (gw, gh), 0); d = ImageDraw.Draw(im)
    for i, x in enumerate(sat):
        tw = d0.textlength(x, font=FONT); d.text((gw / 2 - tw / 2, 10 + i * lh), x, font=FONT, fill=255)
    a = np.asarray(im, np.float32) / 255
    olc = min(1.0, 980 / gw)                       # geniş satır ekrana sığsın
    a = cv2.resize(a, (int(gw * olc), int(gh * olc)), interpolation=cv2.INTER_AREA)
    tam = np.zeros((H, W), np.float32)
    y0 = int(YAZI_Y - a.shape[0] / 2); x0 = int(W / 2 - a.shape[1] / 2)
    tam[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    return tam


MASKE = [maske(m) for _, _, m in SATIR]
_IR = np.random.default_rng(8)
IPLIK = []   # her satır için harf kenarından başlayan iplikler: (x, y, uzunluk, faz)
for _m in MASKE:
    b_ = (_m > 0.5).astype(np.uint8)
    alt = (b_[:-6] == 1) & (b_[6:] == 0)                 # altı boş olan kenar noktaları
    ys_, xs_ = np.nonzero(alt)
    sec = _IR.choice(len(xs_), size=min(70, len(xs_)), replace=False)
    IPLIK.append([(float(xs_[j]), float(ys_[j] + 3), float(_IR.uniform(18, 90)), float(_IR.uniform(0, 6.28))) for j in sec])
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
KUM = cv2.resize(cv2.GaussianBlur(np.random.default_rng(4).random((MH // 4, MW // 4)).astype(np.float32), (0, 0), 1.2),
                 (W, H), interpolation=cv2.INTER_CUBIC)
KUM = (KUM - KUM.min()) / (KUM.max() - KUM.min())


def yazi_yogunluk(i, t):
    """i. satırın mürekkep harfleri: çarpma noktasından yayılarak belirir, sonra dağılıp çöker."""
    a, b, _ = SATIR[i]
    g = t - a
    if g < 0:
        return None
    son = b - a
    cx = W / 2 + (i % 2 * 2 - 1) * 60
    # yayılma: çarpma noktasından uzaklığa göre, gürültülü kenarla (mürekkep kâğıda/suya yürür gibi)
    r = 1300 * (1 - math.exp(-max(0.0, g - 0.2) / 0.35))
    form = math.exp(-max(0.0, g - 0.3) / 0.38)        # 1: dağınık bulut → 0: net harf
    dist = np.sqrt((xx - cx) ** 2 + ((yy - CARPMA_Y) * 1.6) ** 2)
    gor = np.clip((r - dist - KUM * 160) / 60, 0, 1)
    # harfler suda yaşar: kenar haleleri ve yukarı süzülen ince dumanlar; satır bitince hızla dağılıp çöker
    dag = max(0.0, g - son)
    q = g * 0.7
    A = 2.5 + 1.2 * min(g, 3) + 170 * form + 120 * (1 - math.exp(-dag / 0.45))
    dx = cv2.resize(D.fbm(mx_, my_, q) * A, (W, H), interpolation=cv2.INTER_CUBIC)
    dy = cv2.resize(D.fbm(mx_ + 137, my_ + 291, q) * A, (W, H), interpolation=cv2.INTER_CUBIC) + dag * 220
    m = cv2.remap(MASKE[i], xx - dx, yy - dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    cekirdek = cv2.GaussianBlur(m, (0, 0), 0.8 + 24 * form + 10 * (1 - math.exp(-dag / 0.4)))
    hale = cv2.GaussianBlur(m, (0, 0), 7) * np.clip((KUM - 0.25) * 2.2, 0, 1)
    # ince mürekkep iplikleri: harf kenarlarından suya doğru kıvrılarak uzar
    duman = np.zeros((H, W), np.float32)
    for (px, py, uz, faz) in IPLIK[i]:
        L = uz * min(1.0, max(0.0, g - 0.25) / 1.6)
        if L < 4:
            continue
        pts = []; x, y = px, py
        for st in range(int(L / 6)):
            a_ = math.sin(y * 0.03 + faz + q * 1.5) * 0.9 + math.cos(x * 0.02 - q) * 0.4
            x += math.sin(a_) * 4; y += 5.0
            pts.append((x, y))
        if len(pts) > 1:
            P_ = np.array([(px, py)] + pts, np.int32)
            P_[:, 1] = P_[:, 1] + int(dag * 220)
            cv2.polylines(duman, [P_], False, 0.32, 1, cv2.LINE_AA)
    duman = cv2.GaussianBlur(duman, (0, 0), 1.1)
    doku = 0.7 + 0.6 * cv2.resize(np.clip(0.5 + D.fbm(mx_ * 2.6, my_ * 2.6, q) * 1.6, 0, 1), (W, H))
    soluk = math.exp(-dag / 0.35)
    return (cekirdek * doku * (2.4 + 3.0 * form) + hale * 0.9 * (1 - form) + duman) * gor * soluk


def kare(f):
    t = f / FPS
    # düşen damlalar: her satırdan 0,3 sn önce, çarpma noktasına; küçük bulut bırakır
    d = np.zeros((MH, MW), np.float32); hal = np.zeros((MH, MW), np.float32)
    for k, (a, b, _) in enumerate(SATIR):
        td = a - 0.28
        x0 = 0.5 + (k % 2 * 2 - 1) * 60 / W
        g = t - td
        if g < 0:
            continue
        cy_hedef = CARPMA_Y / H * MH
        if g < 0.28:
            y = -6 + (cy_hedef + 6) * (g / 0.28) ** 2
            d += np.exp(-((mx_ - x0 * MW) ** 2 + ((my_ - y) / 1.8) ** 2) / (2 * 3.0 ** 2)) * 5
        else:
            q = g - 0.28
            rr = np.sqrt((mx_ - x0 * MW) ** 2 + ((my_ - cy_hedef) * 3.2) ** 2)
            r = 6 + 90 * (1 - math.exp(-q / 0.35))
            if q < 0.9:
                hal += np.exp(-((rr - r) / 1.1) ** 2) * (1 - q / 0.9) * 0.35
            k2 = 1 - math.exp(-q / 1.4)
            o = (k + 1) * 97.0
            A = 10 + 30 * min(1, q / 2.5)
            wx = mx_ + A * D.fbm(mx_ + o, my_, q); wy = my_ + A * D.fbm(mx_ + 137 + o, my_ + 291, q)
            R = 10 + 75 * (1 - math.exp(-q / 0.45))
            bulut = np.clip(1.05 - np.sqrt(((wx - x0 * MW) / R) ** 2 + ((wy - cy_hedef - 18 * k2) / R) ** 2), 0, 1) ** 1.4
            d += bulut * 1.1 * math.exp(-q / 0.55)
    dd = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)
    for i in range(len(SATIR)):
        y = yazi_yogunluk(i, t)
        if y is not None:
            dd = dd + y
    kost = 0.5 + D.fbm(mx_ * 1.4, my_ * 1.4, t * 0.6, kay=(3, 2)) * 1.2
    fr = D.ZEMIN * (0.97 + 0.05 * cv2.resize(kost, (W, H))[..., None]) * np.exp(-dd[..., None] * D.EMIS * 0.9)
    fr = fr * (1 - cv2.resize(hal, (W, H))[..., None] * 0.25)
    fr = fr * D.VIN
    if t > SURE - 0.4:
        fr = fr * (1 - (t - (SURE - 0.4)) / 0.4 * 0.85)
    fr = fr + D.rng.normal(0, 2.2, (H, W, 1)).astype(np.float32)
    return np.clip(fr, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    if sys.argv[1] == "x":
        ims = [cv2.resize(kare(int(float(v) * FPS)), (270, 480)) for v in sys.argv[2].split(",")]
        cv2.imwrite(sys.argv[3], cv2.cvtColor(np.concatenate(ims, 1), cv2.COLOR_RGB2BGR)); sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-ss", str(T0), "-t", str(SURE), "-i", D.SES, "-af", f"afade=t=in:d=0.05,afade=t=out:st={SURE - 1.2}:d=1.2",
                           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "8M", "-maxrate", "11M",
                           "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                           "-shortest", sys.argv[1]], stdin=subprocess.PIPE)
    for f in range(NF):
        ff.stdin.write(kare(f).tobytes())
    ff.stdin.close(); ff.wait(); print("done")
