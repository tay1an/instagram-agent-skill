"""'Yolun Sonunda' ön dinleti reel'i: şarkı kapağı üzerinde, kapaktaki noktalı yolu ışıktan bir
iz baştan sona yürür; üstteki yıldız şarkıyla atar. Kullanım: yolun_teaser.py <çıktı.mp4> [başla sn] [süre sn]"""
import os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(D, "..", "yolun-sonunda")
SES, KAPAK = os.path.join(K, "yolun-sonunda.wav"), os.path.join(K, "kapak.jpg")
W, H, FPS = 1080, 1920, 30
KY = 330                      # kapağın üst kenarı
# Kapaktaki noktalı yol (2576 px kapak koordinatları), YOLUN'dan SONUNDA'ya.
YOL = [(1233, 1516), (1472, 1509), (1693, 1516), (1877, 1546), (2024, 1601), (2116, 1674), (2134, 1730), (2079, 1785),
       (1950, 1840), (1766, 1884), (1546, 1921), (1325, 1950), (1104, 1980), (920, 2017), (773, 2068), (681, 2127),
       (662, 2190), (718, 2226)]
YILDIZ = (1292, 699)


def yol_noktasi(f):
    """Yol üzerinde 0-1 arası konum (uzunluğa göre)."""
    p = np.array(YOL, np.float32)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    s = f * d[-1]
    i = min(len(d) - 2, int(np.searchsorted(d, s, "right") - 1))
    u = (s - d[i]) / max(1e-6, d[i + 1] - d[i])
    return p[i] * (1 - u) + p[i + 1] * u


def main(cikti, bas=2.0, sure=53.8):
    kap = cv2.cvtColor(cv2.imread(KAPAK), cv2.COLOR_BGR2RGB).astype(np.float32)
    s0 = kap.shape[0]
    # arka plan: kapağın bulanık, koyu hâli ekranı doldurur
    zem = cv2.resize(kap, (H, H))[:, (H - W) // 2:(H - W) // 2 + W]
    zem = cv2.GaussianBlur(zem, (0, 0), 40) * 0.35
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(bas), "-t", str(sure), "-i", SES, "-ac", "1", "-ar", "48000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = int(sure * FPS); k = 48000 // FPS
    rms = np.array([np.sqrt((x[j * k:(j + 1) * k] ** 2).mean() + 1e-9) for j in range(n)])
    rms = np.clip(rms / np.percentile(rms, 95), 0, 1.2)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 40)
    im = Image.new("L", (W, 80), 0)
    ImageDraw.Draw(im).text((W / 2, 40), "11 Aralık'ta Spotify'da", font=f, fill=255, anchor="mm")
    yazi = np.asarray(im, np.float32)[..., None] / 255
    rng = np.random.default_rng(0)
    grains = [rng.normal(0, 4, (H, W, 1)).astype(np.float32) for _ in range(6)]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-ss", str(bas), "-t", str(sure), "-i", SES, "-map", "0:v", "-map", "1:a",
                           "-af", f"afade=t=in:d=0.15,afade=t=out:st={sure - 1.2}:d=1.2",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", "-shortest", cikti], stdin=subprocess.PIPE)
    yol_px = [yol_noktasi(q / 400) for q in range(401)]
    for j in range(n):
        t = j / FPS
        z = 1.0 + 0.07 * t / sure
        boy = int(W * z)
        kk = cv2.resize(kap, (boy, boy), interpolation=cv2.INTER_AREA)
        o = (boy - W) // 2
        kk = kk[o:o + W, o:o + W].copy()
        olc = boy / s0

        def ek(p):
            return (p[0] * olc - o, p[1] * olc - o)

        glow = np.zeros((W // 4, W // 4, 3), np.float32)
        ilerle = min(1.0, t / (sure - 2.5))
        ilerle = ilerle * ilerle * (3 - 2 * ilerle)
        # geçilen yol hafifçe aydınlanır
        for q in range(0, int(ilerle * 400) + 1, 8):
            px, py = ek(yol_px[q])
            cv2.circle(glow, (int(px / 4), int(py / 4)), 3, (255, 200, 130), -1, cv2.LINE_AA)
        # ışık izi
        px, py = ek(yol_noktasi(ilerle))
        cv2.circle(glow, (int(px / 4), int(py / 4)), 7, (255, 230, 180), -1, cv2.LINE_AA)
        cv2.circle(kk, (int(px), int(py)), 7, (255, 245, 225), -1, cv2.LINE_AA)
        # yıldız şarkıyla atar
        sx, sy = ek(YILDIZ)
        cv2.circle(glow, (int(sx / 4), int(sy / 4)), int(6 + 10 * rms[j]), (200, 220, 255), -1, cv2.LINE_AA)
        g = cv2.resize(cv2.GaussianBlur(glow, (0, 0), 6), (W, W))
        kk = np.clip(kk + g * (0.8 + 0.4 * rms[j]), 0, 255)
        fr = zem.copy()
        fr[KY:KY + W] = kk
        a = min(1.0, max(0.0, (t - 1.5) / 0.8)) * 0.85
        bolge = fr[1560:1640]
        fr[1560:1640] = bolge * (1 - yazi * a) + yazi * a * np.array([246, 238, 226], np.float32)
        fr = np.clip(fr + grains[j % 6], 0, 255)
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main(sys.argv[1], *(float(a) for a in sys.argv[2:4]))
    print("done", sys.argv[1])
