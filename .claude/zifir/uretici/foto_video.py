"""Fotoğraftan şarkılı dikey video (reel ya da hikâye): filtre, yavaş yakınlaşma,
film greni, şarkıyla akan sözler ve künye.

Kullanım: foto_video.py <foto> <çıktı.mp4> <başlangıç sn> <filtre> <merkez_x 0-1>
                        [yakınlaştırma] [merkez_y 0-1] [süre sn] [hikaye]
Filtreler kapak_foto.py ile aynıdır. "hikaye" verilirse künyeye "SPOTIFY'DA" eklenir
ve sözler Instagram hikâye arayüzünden uzak, ekranın ortasına yazılır.
"""
import os
import subprocess
import sys

ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["/dev/null"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from PIL import Image  # noqa: E402
import reels as R  # noqa: E402

FILTRE = {
    "kalp": ((8, 1, 4), (230, 80, 90), 0.42),
    "yagmur": ((6, 10, 26), (170, 200, 255), 0.60),
    "sicak-yagmur": ((20, 8, 14), (255, 170, 120), 0.60),
    "agac": ((22, 12, 34), (255, 175, 110), 0.72),
    "gece": ((4, 8, 22), (190, 205, 255), 0.55),
    "mum": ((16, 8, 4), (255, 190, 120), 0.62),
    "gunbatimi": ((24, 12, 36), (255, 170, 110), 0.72),
    "lila": ((14, 12, 36), (255, 200, 190), 0.68),
}
W, H, FPS = 1080, 1920, 30
PAY = 1.08  # yakınlaşma payı


def hazirla(foto, ton, mx, zoom, my):
    """Fotoğrafı 9:16 kırpıp filtreler; yakınlaşma için biraz büyük döndürür."""
    bw, bh = int(W * PAY), int(H * PAY)
    im = Image.open(foto).convert("RGB")
    w, h = im.size
    cw = min(w, round(h * W / H)); ch = round(cw * H / W)
    cw, ch = round(cw / zoom), round(ch / zoom)
    x0 = int(min(max(mx * w - cw / 2, 0), w - cw)); y0 = int(min(max(my * h - ch / 2, 0), h - ch))
    im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((bw, bh), Image.LANCZOS)
    o = np.asarray(im).astype(np.float32)
    g, i, k = FILTRE[ton]
    L = (o @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255
    L = np.clip((L - 0.5) * 1.3 + 0.5, 0, 1) ** (1.15 + (0.6 - k))
    a = (np.array(g, np.float32) * (1 - L) + np.array(i, np.float32) * L) * (0.35 + 0.65 * k)
    a = a * 0.8 + o * 0.2 * k
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    a *= np.clip(1.25 - 0.85 * (((xx - bw / 2) / (bw * .7)) ** 2 + ((yy - bh / 2) / (bh * .62)) ** 2), 0.25, 1)[..., None]
    a *= np.clip(0.5 + (yy / bh) / 0.55 * 0.5, 0.5, 1)[..., None]  # üstü biraz koyulaştır
    return a


def uret(foto, cikti, t0, ton, mx, zoom=1.0, my=0.5, sure=15.0, hikaye=False):
    base = hazirla(foto, ton, mx, zoom, my)
    bh, bw = base.shape[:2]
    t1 = t0 + sure
    soz_y = 0.5 if hikaye else 0.6
    kunye = "ZİFİR  —  UZAK  ·  SPOTIFY'DA" if hikaye else "ZİFİR  —  UZAK"
    tag = R.text_layer(kunye, R.font(R.F_SANS, 30), 960, H * (soz_y + 0.115))
    lyr = [(s - t0, e - t0, R.text_layer(txt, R.font(R.F_SERIF, 60, 500), 900, H * soz_y))
           for s, e, txt in R.LYRICS if e > t0 and s < t1]
    # İlk saniye kancası: ilk söz satırı ilk karede tam görünür, siyahtan açılış yok.
    lyr = [(-1.0 if k == 0 and s < 1.2 else s, e, L) for k, (s, e, L) in enumerate(lyr)]
    rng = np.random.default_rng(0)
    grains = [rng.normal(0, 6, (H, W, 1)).astype(np.float32) for _ in range(6)]
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-ss", f"{t0}", "-t", f"{sure}", "-i", R.SONG, "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:d=0.08,afade=t=out:st={sure - 0.9}:d=0.9",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "3500k", "-bufsize", "7000k",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
        "-shortest", cikti], stdin=subprocess.PIPE)
    n = int(sure * FPS)
    for j in range(n):
        t = j / FPS
        z = 1.0 + 0.07 * t / sure
        cw, ch = bw / z, bh / z
        x0, y0 = (bw - cw) / 2, (bh - ch) / 2
        M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        fr = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR)
        fr = np.clip(fr + grains[j % 6], 0, 255)
        R.comp_text(fr, tag, 0.8, (235, 225, 215))
        for s, e, L in lyr:
            if s - 0.05 <= t <= e:
                a = min(1, (t - s + 0.05) / 0.25, (e - t) / 0.2)
                R.comp_text(fr, L, max(0, a), (255, 246, 235), int(12 * (1 - min(1, (t - s + 0.05) / 0.4))))
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    foto, cikti, t0, ton, mx = ARGS[0], ARGS[1], float(ARGS[2]), ARGS[3], float(ARGS[4])
    zoom = float(ARGS[5]) if len(ARGS) > 5 else 1.0
    my = float(ARGS[6]) if len(ARGS) > 6 else 0.5
    sure = float(ARGS[7]) if len(ARGS) > 7 else 15.0
    uret(foto, cikti, t0, ton, mx, zoom, my, sure, hikaye=len(ARGS) > 8 and ARGS[8] == "hikaye")
    print("done", cikti, flush=True)
