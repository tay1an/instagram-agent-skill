"""'İki şey' reel'i, minimal animasyon: koyu zeminde lamba gibi atan bir nokta, kelime kelime
gelen yazılar, ikiye ayrılan noktalar arasında şarkının kendi dalga formu, söylendikçe yanan
sözler ve sonda gerçek zamanı gösteren bir müzik çalar kartı.
Kullanım: iki_sey_animasyon.py <çıktı.mp4>"""
import os, subprocess, sys
ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["/dev/null"]
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402
import reels as R  # noqa: E402

W, H, FPS = 1080, 1920, 30
T0, SURE = 48.9, 20.4
ITALIK = os.path.join(D, "fonts", "PlayfairDisplay-Italic[wght].ttf")
SERIF = os.path.join(D, "fonts", "PlayfairDisplay[wght].ttf")
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
KREM = np.array([246, 238, 226], np.float32)
SICAK = np.array([255, 110, 70], np.float32)
CX, CY = W / 2, H * 0.56


def fnt(yol, boy, ag=None):
    f = ImageFont.truetype(yol, boy)
    if ag:
        f.set_variation_by_axes([ag])
    return f


def kelime_sprite(s, f):
    x0, y0, x1, y1 = f.getbbox(s)
    im = Image.new("L", (x1 - x0 + 8, y1 - y0 + 8), 0)
    ImageDraw.Draw(im).text((4 - x0, 4 - y0), s, font=f, fill=255)
    return np.asarray(im, np.float32) / 255, f.getlength(s), y0


def satirlar(metin, f, gen=900, y=0.3, aralik=1.2):
    """Kelimeleri satırlara dizer: [(sprite, x, y)] (sol üst köşe)."""
    bosluk = f.getlength(" ")
    kel = [kelime_sprite(k, f) + (k,) for k in metin.split()]
    sat, cur, cw = [], [], 0
    for k in kel:
        w = k[1] if not cur else cw + bosluk + k[1]
        if w > gen and cur:
            sat.append(cur); cur, w = [k], k[1]
        else:
            cur.append(k)
        cw = w
    sat.append(cur)
    lh = f.size * aralik
    out = []
    yy = H * y - lh * len(sat) / 2
    for s in sat:
        tw = sum(k[1] for k in s) + bosluk * (len(s) - 1)
        x = W / 2 - tw / 2
        for spr, kw, oy, txt in s:
            out.append((spr, x, yy + oy, txt))
            x += kw + bosluk
        yy += lh
    return out


def koy(fr, spr, x, y, al, renk=KREM):
    if al <= 0:
        return
    x, y = int(round(x)), int(round(y))
    h, w = spr.shape
    ys, xs = max(0, -y), max(0, -x)
    y1, x1 = min(h, H - y), min(w, W - x)
    if y1 <= ys or x1 <= xs:
        return
    a = spr[ys:y1, xs:x1, None] * al
    bol = fr[y + ys:y + y1, x + xs:x + x1]
    bol[:] = bol * (1 - a) + a * renk


def isik(fr, x, y, r, guc, renk=SICAK):
    """Yumuşak parlayan nokta."""
    R_ = int(r * 16)
    x0, y0 = int(x) - R_, int(y) - R_
    yy, xx = np.mgrid[0:2 * R_, 0:2 * R_].astype(np.float32)
    d2 = (xx - (x - x0)) ** 2 + (yy - (y - y0)) ** 2
    g = (np.exp(-d2 / (2 * r * r)) + 0.35 * np.exp(-d2 / (2 * (r * 4) ** 2))) * guc
    ys, xs = max(0, -y0), max(0, -x0)
    sl = fr[y0 + ys:y0 + 2 * R_, x0 + xs:x0 + 2 * R_]
    gg = g[ys:ys + sl.shape[0], xs:xs + sl.shape[1], None]
    sl += gg * renk
    core = np.exp(-d2 / (2 * (r * 0.35) ** 2))[ys:ys + sl.shape[0], xs:xs + sl.shape[1], None] * guc
    sl += core * 255


def yumusak(t):
    t = float(np.clip(t, 0, 1))
    return t * t * (3 - 2 * t)


def ses():
    ham = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(T0), "-t", str(SURE + 0.5), "-i", R.SONG,
                          "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(ham, np.int16).astype(np.float32) / 32768


def main(cikti):
    x = ses()
    n = int(SURE * FPS); k = 48000 // FPS
    rms = np.array([np.sqrt((x[j * k:(j + 1) * k] ** 2).mean() + 1e-9) for j in range(n)])
    rms = np.clip(rms / np.percentile(rms, 95), 0, 1.2)
    # zemin: sıcak siyah, hafif vinyet
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.clip(1.15 - 0.9 * (((xx - W / 2) / W) ** 2 + ((yy - H * 0.5) / (H * 0.8)) ** 2), 0.3, 1)
    zemin = (np.array([16, 12, 13], np.float32) * v[..., None])
    rng = np.random.default_rng(0)
    grains = [rng.normal(0, 5, (H, W, 1)).astype(np.float32) for _ in range(6)]

    fB = fnt(ITALIK, 92, 500)
    hook = satirlar("Bugün duyman gereken iki şey var.", fB, y=0.3)
    bir = satirlar("Sen çok değerlisin.", fB, y=0.3)
    iki = satirlar("Bunu sana bir şarkıyla söyledim.", fB, y=0.3)
    sayi_f = fnt(SERIF, 520, 400)
    s1, s2 = kelime_sprite("1", sayi_f), kelime_sprite("2", sayi_f)
    fK = fnt(ITALIK, 84, 500)
    kar1 = satirlar("Oysa seni sana anlatan ben idim", fK, y=0.29)
    kar2 = satirlar("Ben eğer yok isem sen de olmazsın dedim", fK, y=0.29)
    LYR = {l[2]: (l[0] - T0, l[1] - T0) for l in R.LYRICS if 58 < l[0] < 67}
    ka1 = LYR["Oysa seni sana anlatan ben idim"]; ka2 = LYR["Ben eğer yok isem sen de olmazsın dedim"]
    kucuk = fnt(SANS, 34)
    etiket_bir, etiket_iki = kelime_sprite("BİR", kucuk), kelime_sprite("İKİ", kucuk)
    uzak = kelime_sprite("Uzak", fnt(ITALIK, 150, 500)); zifir = kelime_sprite("ZİFİR", fnt(SANS, 40))
    alt = kelime_sprite("Şimdi Spotify'da  ·  link profilde", fnt(SANS, 38))
    zaman_f = fnt(SANS, 32)

    def kelimeler(fr, liste, bas, t, adim=0.16, op=1.0):
        for i, (spr, kx, ky, _) in enumerate(liste):
            a = yumusak((t - bas - i * adim) / 0.35)
            koy(fr, spr, kx, ky + 22 * (1 - a), a * op)

    def karaoke(fr, liste, aralik, t, op):
        top = sum(len(w[3]) for w in liste)
        s, e = aralik
        bit = s
        for spr, kx, ky, txt in liste:
            b0 = bit; bit += (e - s) * len(txt) / top
            yan = yumusak((t - b0) / 0.18)
            renk = KREM * (0.28 + 0.72 * yan) + SICAK * 0.0
            koy(fr, spr, kx, ky, op, renk)

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-ss", str(T0), "-t", str(SURE), "-i", R.SONG, "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:d=0.08,afade=t=out:st={SURE - 1.0}:d=1.0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "6000k", "-bufsize", "12000k",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
        "-shortest", cikti], stdin=subprocess.PIPE)
    dalga_x = np.linspace(-1, 1, 360)
    for j in range(n):
        t = j / FPS
        fr = zemin.copy()
        r = rms[j]
        # --- yazılar ---
        if t < 2.6:
            op = 1 - yumusak((t - 2.2) / 0.4)
            for spr, kx, ky, _ in hook:
                koy(fr, spr, kx, ky, op)
        if 2.4 <= t < 6.3:
            op = yumusak((t - 2.4) / 0.4) * (1 - yumusak((t - 5.9) / 0.4))
            koy(fr, s1[0], W / 2 - s1[1] / 2, H * 0.55 - 330, 0.07 * op)
            koy(fr, etiket_bir[0], W / 2 - etiket_bir[1] / 2, H * 0.3 - 140, 0.75 * op)
            kelimeler(fr, bir, 2.6, t, op=op)
        if 6.0 <= t < 10.2:
            op = yumusak((t - 6.0) / 0.4) * (1 - yumusak((t - 9.8) / 0.35))
            koy(fr, s2[0], W / 2 - s2[1] / 2, H * 0.55 - 330, 0.07 * op)
            koy(fr, etiket_iki[0], W / 2 - etiket_iki[1] / 2, H * 0.3 - 140, 0.75 * op)
            kelimeler(fr, iki, 6.2, t, op=op)
        if 9.9 <= t < 13.95:
            op = yumusak((t - 9.9) / 0.3) * (1 - yumusak((t - 13.6) / 0.3))
            karaoke(fr, kar1, ka1, t, op)
        if 13.7 <= t < 17.6:
            op = yumusak((t - 13.7) / 0.3) * (1 - yumusak((t - 17.2) / 0.35))
            karaoke(fr, kar2, ka2, t, op)
        # --- ışık: tek nokta → ikiye ayrılır → aralarında dalga ---
        ayr = yumusak((t - 7.2) / 1.6)
        cik = 1 - yumusak((t - 17.3) / 0.5)
        yarim = 330 * ayr
        if t < 17.8:
            guc = (0.55 + 0.6 * r) * cik
            if ayr < 0.02:
                isik(fr, CX, CY, 16 + 6 * r, guc)
            else:
                isik(fr, CX - yarim, CY, 12 + 4 * r, guc)
                isik(fr, CX + yarim, CY, 12 + 4 * r, guc)
            if ayr > 0.05:
                bas = int(j * 48000 / FPS)
                parca = x[bas:bas + 1600] if bas + 1600 <= len(x) else np.zeros(1600, np.float32)
                ornek = np.interp(np.linspace(0, len(parca) - 1, 360), np.arange(len(parca)), parca)
                zarf = np.cos(dalga_x * np.pi / 2) ** 2
                ys = CY - ornek * 900 * zarf * (0.6 + 0.6 * r)
                xs = CX + dalga_x * yarim * 0.96
                im = Image.new("L", (W, H), 0)
                ImageDraw.Draw(im).line(list(zip(xs, ys)), fill=255, width=3)
                m = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32)[..., None] / 255
                al = min(1.0, (ayr - 0.05) * 3) * cik
                fr = fr * (1 - m * al) + m * al * (KREM * 0.85 + SICAK * 0.15)
        # --- son kart: çalar ---
        if t >= 17.5:
            op = yumusak((t - 17.5) / 0.5)
            koy(fr, uzak[0], W / 2 - uzak[1] / 2, H * 0.36, op)
            koy(fr, zifir[0], W / 2 - zifir[1] / 2, H * 0.36 + 200, 0.75 * op)
            ilerle = (T0 + t) / 176.0
            bx0, bx1, by = 140, W - 140, int(H * 0.55)
            fr[by - 2:by + 2, bx0:bx1] = fr[by - 2:by + 2, bx0:bx1] * (1 - 0.3 * op) + KREM * 0.3 * op
            xe = int(bx0 + (bx1 - bx0) * ilerle)
            fr[by - 3:by + 3, bx0:xe] = fr[by - 3:by + 3, bx0:xe] * (1 - op) + KREM * op
            isik(fr, xe, by, 7, 0.9 * op, KREM)
            s = int(T0 + t)
            koy(fr, kelime_sprite(f"{s // 60}:{s % 60:02d}", zaman_f)[0], bx0, by + 30, 0.7 * op)
            koy(fr, kelime_sprite("2:56", zaman_f)[0], bx1 - zaman_f.getlength("2:56"), by + 30, 0.7 * op)
            # duraklat simgesi (çalıyor)
            px, py = int(W / 2), int(H * 0.62)
            for dx in (-22, 10):
                fr[py:py + 64, px + dx:px + dx + 14] = fr[py:py + 64, px + dx:px + dx + 14] * (1 - op) + KREM * op
            koy(fr, alt[0], W / 2 - alt[1] / 2, H * 0.71, 0.85 * op)
        fr = np.clip(fr + grains[j % 6], 0, 255)
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main(ARGS[0])
    print("done", ARGS[0], flush=True)
