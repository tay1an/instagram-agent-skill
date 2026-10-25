import json, subprocess, sys, os
from PIL import Image
OUT=os.path.abspath(sys.argv[2] if len(sys.argv)>2 else ".claude/instagram/gorseller")
CSS="""*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;font-family:'Inter',sans-serif;position:relative;
background:radial-gradient(ellipse at 50% 55%,#fffaf0 0%,#f6ead4 60%,#ead6b4 100%);color:#5a2a12}
.band{position:absolute;left:0;right:0;height:140px;background:#b3151b}
.band.top{top:0}.band.bot{bottom:0}
.band:after{content:"";position:absolute;left:0;right:0;height:6px;background:#c9a24a}
.band.top:after{bottom:-14px}.band.bot:after{top:-14px}
.wrap{position:absolute;top:470px;bottom:330px;left:90px;right:90px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:26px}
.kick{font-size:44px;font-weight:600;letter-spacing:6px;color:#b07a42;text-transform:uppercase}
.t{font-size:74px;font-weight:800;line-height:1.12}
.big{font-family:'Inter Display';font-weight:900;color:#b3151b;font-size:200px;letter-spacing:-8px;line-height:.95}
.s{font-size:50px;font-weight:500;line-height:1.3;color:#6b3a1c}
.r{color:#b3151b}
.e{font-family:'Noto Color Emoji'}
.photo{width:430px;border-radius:26px;border:12px solid #fffaf0;box-shadow:0 26px 50px rgba(90,42,18,.28),0 0 0 2px #c9a24a;transform:rotate(-2deg)}
.foot{position:absolute;bottom:200px;width:100%;text-align:center;font-size:40px;font-weight:600;color:#8a5a2e}
.logo{position:absolute;top:190px;left:50%;transform:translateX(-50%);width:430px}
.seed{position:absolute;width:18px;height:30px;border-radius:50%;background:#fffaf0;box-shadow:inset -3px -4px 0 rgba(150,105,55,.25);opacity:.8}
"""
SEEDS=[[70,320,20],[980,300,-30],[60,700,40],[1010,820,-35],[110,1380,15],[960,1450,-20],[200,1660,30],[880,1640,-25]]
def page(body, seeds=True):
    s="".join(f'<div class="seed" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"></div>' for x,y,r in SEEDS) if seeds else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="band top"></div><img class="logo" src="logo.png">{s}{body}<div class="band bot"></div></body></html>'
E=lambda x:f'<span class="e">{x}</span>'
stories=json.load(open(sys.argv[1]))
for st in stories:
    open("tmp.html","w").write(page(st["html"], st.get("seeds",True)))
    png=f"{st['id']}.png"
    subprocess.run(["node","shot.js",os.path.abspath("tmp.html"),os.path.abspath(png)],check=True)
    Image.open(png).convert("RGB").save(f"{OUT}/{st['id']}.jpg",quality=92)
    print("ok",st["id"])
