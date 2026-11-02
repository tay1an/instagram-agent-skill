"""'İki şey' carousel'inin reel hâli: 5 sahne, Ken Burns, yazılar süzülerek gelir, sahneler
arası geçiş, son sahnede şarkıyla atan ses çubukları. Ses: Uzak 48.9 sn'den; 4. sahne
"Oysa seni sana anlatan ben idim" satırıyla aynı anda gelir.
Kullanım: iki_sey_reel.py <çıktı.mp4> <kapak.jpg>"""
import os, subprocess, sys
ARGS = sys.argv[1:]
sys.argv = sys.argv[:1] + ["/dev/null"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from PIL import Image  # noqa: E402
import reels as R  # noqa: E402
import foto_video as FV  # noqa: E402

W, H, FPS = 1080, 1920, 30
T0, SURE = 48.9, 17.7
S = "stok/"
GECIS = 0.3
ITALIK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PlayfairDisplay-Italic[wght].ttf")
# (başlangıç, bitiş, foto, filtre, mx, zoom, my, etiket, büyük yazı, alt yazı, yazı y)
SAHNE = [
    (0.0, 3.4, S + "07-sahil.jpg", "gunbatimi", 0.5, 1.0, 0.5, "", "Bugün duyman gereken iki şey var.", "", 0.34),
    (3.4, 6.8, S + "03-eller.jpg", "lila", 0.5, 1.0, 0.5, "BİR", "Sen çok değerlisin.", "Bunu sana kimse söylemediyse, şimdi duydun.", 0.3),
    (6.8, 10.1, S + "02-sehir.jpg", "mum", 0.5, 1.0, 0.5, "İKİ", "Bunu sana bir şarkıyla söyledim.", "ZİFİR  —  UZAK", 0.28),
    (10.1, 13.7, S + "09-lamba.jpg", "dogal", 0.5, 1.0, 0.5, "", "Oysa seni sana anlatan ben idim.", "— Uzak", 0.66),
    (13.7, SURE, S + "05-iskele.jpg", "yagmur", 0.46, 2.0, 0.45, "", "Uzak şimdi Spotify'da.", "Kulaklığını tak, sonuna kadar dinle.", 0.3),
]


def zarf():
    """Şarkının kare başına ses yüksekliği (0-1), çubuklar için."""
    ham = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(T0), "-t", str(SURE), "-i", R.SONG,
                          "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(ham, np.int16).astype(np.float32) / 32768
    n = int(SURE * FPS); k = len(x) // n
    r = np.sqrt((x[:n * k].reshape(n, k) ** 2).mean(1))
    return np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1)


def sahne_hazirla(sc):
    t0, t1, foto, ton, mx, zoom, my, etk, buyuk, alt, ty = sc
    FV.W, FV.H = W, H
    a = FV.hazirla(foto, ton, mx, zoom, my)
    yy = np.mgrid[0:a.shape[0], 0:a.shape[1]][0].astype(np.float32) / a.shape[0]
    a = a * np.clip(0.6 + 1.5 * np.abs(yy - ty), 0.6, 1)[..., None]  # yazının arkası koyu
    kat = []
    if etk:
        kat.append((0.0, R.text_layer(etk, R.font(R.F_SANS, 34), 900, H * ty - 150), (235, 225, 215), 0.8))
    kat.append((0.15, R.text_layer(buyuk, R.font(ITALIK, 100, 500), 920, H * ty), (255, 246, 235), 1.0))
    if alt:
        kat.append((0.6, R.text_layer(alt, R.font(R.F_SANS, 40), 900, H * ty + 180), (235, 225, 215), 0.85))
    return a, kat


def kare(a, u, sure):
    bh, bw = a.shape[:2]
    z = 1.0 + 0.06 * u / sure
    cw, ch = bw / z, bh / z
    x0, y0 = (bw - cw) / 2 + 10 * u / sure, (bh - ch) / 2
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
    return cv2.warpAffine(a.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR)


def ciz(sc, hazir, t, ilk):
    t0, t1 = sc[0], sc[1]
    a, kat = hazir
    u = t - t0
    fr = kare(a, u, t1 - t0)
    for gec, lay, renk, op in kat:
        g = u - gec
        if ilk and t0 == 0:  # ilk kare kancası: ilk sahnenin yazısı baştan tam görünür
            g = 1.0
        al = np.clip(g / 0.45, 0, 1)
        al = al * al * (3 - 2 * al)
        R.comp_text(fr, lay, al * op, renk, int(28 * (1 - al)))
    return fr


def cubuklar(fr, seviye, j, al):
    """Son sahnede şarkıyla atan beş ince çubuk."""
    x0, yb = W / 2 - 2 * 34, int(H * 0.3 + 300)
    for i in range(5):
        h = 18 + 90 * seviye[max(0, j - 2 * i % 5)] * (0.55 + 0.45 * np.sin(i * 1.7 + j * 0.21) ** 2)
        x = int(x0 + i * 34)
        y1 = int(yb - h)
        fr[y1:yb, x - 5:x + 5] = fr[y1:yb, x - 5:x + 5] * (1 - al) + np.array([255, 246, 235], np.float32) * al


def main(cikti, kapak):
    hazir = [sahne_hazirla(sc) for sc in SAHNE]
    sev = zarf()
    rng = np.random.default_rng(0)
    grains = [rng.normal(0, 6, (H, W, 1)).astype(np.float32) for _ in range(6)]
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-ss", str(T0), "-t", str(SURE), "-i", R.SONG, "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:d=0.08,afade=t=out:st={SURE - 0.9}:d=0.9",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "5000k", "-bufsize", "10000k",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
        "-shortest", cikti], stdin=subprocess.PIPE)
    n = int(SURE * FPS)
    for j in range(n):
        t = j / FPS
        i = max(k for k, sc in enumerate(SAHNE) if sc[0] <= t)
        fr = ciz(SAHNE[i], hazir[i], t, True)
        if i > 0 and t - SAHNE[i][0] < GECIS:  # önceki sahneden yumuşak geçiş
            w = (t - SAHNE[i][0]) / GECIS
            fr = ciz(SAHNE[i - 1], hazir[i - 1], t, True) * (1 - w) + fr * w
        if i == len(SAHNE) - 1:
            cubuklar(fr, sev, j, float(np.clip((t - SAHNE[i][0] - 0.9) / 0.4, 0, 1)))
        fr = np.clip(fr + grains[j % 6], 0, 255)
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    # Kapak: yazısız, insanlı ilk sahne.
    a = hazir[0][0]
    bh, bw = a.shape[:2]
    Image.fromarray(np.clip(a[(bh - H) // 2:(bh - H) // 2 + H, (bw - W) // 2:(bw - W) // 2 + W], 0, 255).astype(np.uint8)).save(kapak, quality=92)


if __name__ == "__main__":
    main(ARGS[0], ARGS[1])
    print("done", ARGS[0], flush=True)
