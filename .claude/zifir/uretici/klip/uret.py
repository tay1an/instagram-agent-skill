"""Uzak klibini üretir. Kullanım: uret.py <çıktı.mp4> [başla sn] [bitir sn] [ölçek]"""
import os, subprocess, sys
from multiprocessing import Pool
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import numpy as np  # noqa: E402
import cv2  # noqa: E402

FPS = 30
SONG = os.path.join(D, "..", "uzak.m4a")


def parca(arg):
    i, t0, t1, yol, olcek = arg
    import sahneler as S
    w, h = int(S.W * olcek) // 2 * 2, int(S.H * olcek) // 2 * 2
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", yol],
                          stdin=subprocess.PIPE)
    rng = np.random.default_rng(i)
    for j in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        img = S.kare(j / FPS).astype(np.float32)
        img += rng.normal(0, 3.5, (S.H, S.W, 1)).astype(np.float32)  # film greni
        img = np.clip(img, 0, 255).astype(np.uint8)
        if olcek != 1:
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    return yol


def main():
    cikti = sys.argv[1]
    bas = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    son = float(sys.argv[3]) if len(sys.argv) > 3 else 176.8
    olcek = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    n = 8
    sinir = [bas + (son - bas) * k / n for k in range(n + 1)]
    sinir = [round(x * FPS) / FPS for x in sinir]
    tmp = cikti + ".parca"
    os.makedirs(tmp, exist_ok=True)
    isler = [(k, sinir[k], sinir[k + 1], f"{tmp}/{k:02d}.mp4", olcek) for k in range(n)]
    with Pool(4) as p:
        parcalar = p.map(parca, isler)
    with open(f"{tmp}/liste.txt", "w") as f:
        f.writelines(f"file '{os.path.abspath(x)}'\n" for x in parcalar)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/liste.txt",
                    "-ss", str(bas), "-t", str(son - bas), "-i", SONG, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", cikti], check=True)
    print("done", cikti)


if __name__ == "__main__":
    main()
