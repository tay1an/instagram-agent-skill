import json, subprocess, sys, os
from PIL import Image
OUT=os.path.abspath(sys.argv[2] if len(sys.argv)>2 else "/home/user/instagram-agent-skill/.claude/instagram/gorseller")
CSS="""*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;font-family:'Inter',sans-serif;position:relative;
background:radial-gradient(ellipse at 50% 50%,#fffaf0 0%,#f6ead4 65%,#ead6b4 100%);color:#5a2a12}
.bt{position:absolute;top:0;left:0;right:0;height:22px;background:#b3151b;border-bottom:5px solid #c9a24a}
.bb{position:absolute;bottom:0;left:0;right:0;height:22px;background:#b3151b;border-top:5px solid #c9a24a}
.logo{position:absolute;top:70px;left:50%;transform:translateX(-50%);width:250px}
.logo.big{width:520px;top:110px}
.wrap{position:absolute;top:300px;bottom:150px;left:90px;right:90px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:30px}
.kick{font-size:38px;font-weight:600;letter-spacing:6px;color:#b07a42;text-transform:uppercase}
.t{font-size:78px;font-weight:800;line-height:1.1}
.big{font-family:'Inter Display';font-weight:900;color:#b3151b;font-size:220px;letter-spacing:-8px;line-height:.9}
.s{font-size:46px;font-weight:500;line-height:1.35;color:#6b3a1c}
.r{color:#b3151b}.g{color:#b07a42}
.e{font-family:'Noto Color Emoji'}
.n{font-family:'Inter Display';font-weight:900;font-size:120px;color:#c9a24a;line-height:1}
.photo{width:430px;border-radius:24px;border:12px solid #fffaf0;box-shadow:0 22px 44px rgba(90,42,18,.28),0 0 0 2px #c9a24a;transform:rotate(-2deg)}
.foot{position:absolute;bottom:62px;width:100%;text-align:center;font-size:34px;font-weight:600;color:#8a5a2e}
.pg{position:absolute;bottom:62px;right:70px;font-size:30px;font-weight:600;color:#b07a42}
.list{text-align:left;font-size:46px;line-height:1.6;font-weight:500}
.list b{color:#b3151b}
"""
def page(body, big=False):
    return f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="bt"></div><img class="logo{" big" if big else ""}" src="logo.png">{body}<div class="bb"></div></body></html>'
data=json.load(open(sys.argv[1]))
for car in data:
    n=len(car["slides"])
    for i,sl in enumerate(car["slides"],1):
        body=sl+(f'<div class="pg">{i}/{n}</div>' if i>1 else "")
        open("tmp2.html","w").write(page(body, big=False))
        png=f'{car["id"]}-{i}.png'
        subprocess.run(["node","shot2.js",os.path.abspath("tmp2.html"),os.path.abspath(png),"1080","1350"],check=True)
        Image.open(png).convert("RGB").save(f'{OUT}/{car["id"]}-{i}.jpg',quality=92)
    print("ok",car["id"],n)
