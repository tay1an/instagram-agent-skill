"""plan_2.py'deki bütün videoları ve kapakları üretir. Kullanım: plan_2_uret.py <çıktı klasörü> <parça> <parça sayısı>"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_2 as P
out, k, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
FV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto_video.py")
KF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kapak_foto.py")
isler = [("r", x) for x in P.REEL] + [("h", x) for x in P.HIKAYE]
for i, (tur, x) in enumerate(isler):
    if i % n != k:
        continue
    if tur == "r":
        ad, _, foto, ton, mx, zoom, my, t0, soz = x
        subprocess.run(["python3", "-I", FV, foto, f"{out}/{ad}.mp4", str(t0), ton, str(mx), str(zoom), str(my), "15"], check=True)
        subprocess.run(["python3", "-I", KF, foto, f"{out}/{ad}-kapak.jpg", soz, str(mx), "0.27", ton, str(zoom), str(my)], check=True)
    else:
        ad, _, foto, ton, mx, zoom, my, t0 = x
        subprocess.run(["python3", "-I", FV, foto, f"{out}/{ad}.mp4", str(t0), ton, str(mx), str(zoom), str(my), "15", "hikaye"], check=True)
