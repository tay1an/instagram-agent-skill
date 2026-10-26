"""Zifir - Uzak: full-length 16:9 lyric video. Usage: lyricvideo.py <chunk_idx> <n_chunks> | concat"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv, ARGS = sys.argv[:1] + ["/dev/null"], sys.argv[1:]
import numpy as np, cv2
from PIL import Image
import reels as R

DIKEY = os.environ.get("ORIENT") == "dikey"
W, H, FPS = (1080, 1920, 30) if DIKEY else (1920, 1080, 30)
R.W, R.H, R.BW, R.BH = W, H, int(W * 1.08), int(H * 1.08)
BW, BH = R.BW, R.BH
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "lyric-dikey" if DIKEY else "lyric")
DUR = 176.8
XF = 1.6  # crossfade length

TIMELINE = [  # (start, end, scene factory) - scenes follow the lyric imagery
    (0.0, 9.0, lambda: R.Night()),                                   # intro
    (9.0, 24.4, lambda: R.Heart()),                                  # elindeki kalbi / kor yara
    (24.4, 43.6, lambda: R.Candle()),                                # alevin içinde yanması
    (43.6, 59.0, lambda: R.Sunset()),                                # ufuk daldırır beni
    (59.0, 66.4, lambda: R.Rain()),                                  # oysa seni sana anlatan
    (66.4, 83.0, lambda: R.Trees()),                                 # yan yana ağacız
    (83.0, 103.2, lambda: R.Night()),                                # instrumental
    (103.2, 123.4, lambda: R.Sunset("lilac", False, True)),          # sevgili sevgilim / bir sabah
    (123.4, 138.6, lambda: R.Sunset()),                              # ufuk (2)
    (138.6, 145.4, lambda: R.Rain(warm=True, seed=5)),               # oysa seni (2)
    (145.4, 162.0, lambda: R.Trees()),                               # yan yana ağacız (2)
    (162.0, DUR, lambda: R.Night()),                                 # outro
]

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = np.clip(1.25 - 0.8 * (((xx - W / 2) / (W * .7)) ** 2 + ((yy - H / 2) / (H * .75)) ** 2), 0.35, 1)[..., None]
_rng = np.random.default_rng(0)
GRAIN = [_rng.normal(0, 6, (H, W, 1)).astype(np.float32) for _ in range(6)]

LYR = [(s, e, R.text_layer(txt, R.font(R.F_SERIF, 60 if DIKEY else 66, 500), 900 if DIKEY else 1500, H * (0.62 if DIKEY else 0.83)))
       for s, e, txt in R.LYRICS]
TITLE = R.text_layer("Uzak", R.font(R.F_ITAL, 150, 500), 900 if DIKEY else 1500, H * (0.24 if DIKEY else 0.45))
ARTIST = R.text_layer("Z İ F İ R", R.font(R.F_SANS, 38), 900, H * (0.31 if DIKEY else 0.58))
TITLE_WINDOWS = [(1.0, 8.4), (164.0, DUR)]

_cache = {}


def scene(i):
    if i not in _cache:
        _cache[i] = TIMELINE[i][2]()
    return _cache[i]


def scene_frame(i, t):
    s0, s1, _ = TIMELINE[i]
    sc = scene(i)
    f = sc.base.copy()
    sc.anim(f, t)
    z = 1.0 + 0.06 * np.clip((t - s0 + XF) / (s1 - s0 + 2 * XF), 0, 1)
    cw, ch = BW / z, BH / z
    x0, y0 = (BW - cw) / 2, (BH - ch) / 2
    M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR)


def frame(t, i_frame):
    active = []
    for i, (s0, s1, _) in enumerate(TIMELINE):
        if s0 - XF / 2 <= t < s1 + XF / 2:
            a = 1.0
            if i > 0 and t < s0 + XF / 2:
                a = (t - (s0 - XF / 2)) / XF
            if i < len(TIMELINE) - 1 and t > s1 - XF / 2:
                a = min(a, ((s1 + XF / 2) - t) / XF)
            active.append((i, np.clip(a, 0, 1)))
    fr = np.zeros((H, W, 3), np.float32)
    for i, a in active:
        fr += scene_frame(i, t) * a
    fr = np.clip(np.clip(fr, 0, 255) * VIGN + GRAIN[i_frame % 6], 0, 255)
    for w0, w1 in TITLE_WINDOWS:
        if w0 <= t <= w1:
            a = min(1, (t - w0) / 1.2, (w1 - t) / 1.2)
            R.comp_text(fr, TITLE, a, (255, 246, 235))
            R.comp_text(fr, ARTIST, a * 0.85, (235, 225, 215))
    for s, e, L in LYR:
        if s - 0.05 <= t <= e:
            a = min(1, (t - s + 0.05) / 0.25, (e - t) / 0.2)
            rise = int(12 * (1 - min(1, (t - s + 0.05) / 0.4)))
            R.comp_text(fr, L, max(0, a), (255, 246, 235), rise)
    fade = min(1, t / 1.5, (DUR - t) / 2.0)
    return fr * max(0, fade)


def render_chunk(k, n):
    os.makedirs(OUTD, exist_ok=True)
    total = int(DUR * FPS)
    a, b = total * k // n, total * (k + 1) // n
    out = os.path.join(OUTD, f"part{k}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b):
        t = i / FPS
        for j, (s0, s1, _) in enumerate(TIMELINE):  # free scenes we are done with
            if j in _cache and t > s1 + XF:
                del _cache[j]
        fr = frame(t, i)
        if i == int(5 * FPS):
            Image.fromarray(fr.astype(np.uint8)).save(os.path.join(OUTD, "kapak.jpg"), quality=92)
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()
    print("done chunk", k, flush=True)


def concat(n):
    lst = os.path.join(OUTD, "parts.txt")
    with open(lst, "w") as f:
        f.writelines(f"file 'part{k}.mp4'\n" for k in range(n))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", R.SONG,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", "-shortest", os.path.join(OUTD, "Zifir - Uzak (Lyrics Video).mp4")], check=True)


if __name__ == "__main__":
    if ARGS[0] == "concat":
        concat(int(ARGS[1]))
    elif ARGS[0] == "still":
        os.makedirs(OUTD, exist_ok=True)
        ims = [cv2.resize(frame(t, 0), (W // 4, H // 4)) for t in map(float, ARGS[1:])]
        Image.fromarray(np.concatenate([np.concatenate(ims[i:i + 3], 1) for i in range(0, len(ims), 3)], 0).astype(np.uint8)).save(os.path.join(OUTD, "stills.jpg"))
    else:
        render_chunk(int(ARGS[0]), int(ARGS[1]))
