import re, subprocess, os, html, sys
from PIL import Image
exec(open('dmtarif.py').read().split("CSS=")[0])  # parse, body_html, parts
W,H=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
CSS=f"""*{{margin:0;padding:0;box-sizing:border-box}}body{{width:{W}px;height:{H}px;overflow:hidden;font-family:'Inter',sans-serif;background:radial-gradient(ellipse at 50% 45%,#fffaf0 0%,#f6ead4 70%,#ead6b4 100%);color:#4a2510;position:relative}}
.band{{position:absolute;left:0;right:0;height:40px;background:#b3151b}}.top{{top:0;border-bottom:5px solid #c9a24a}}.bot{{bottom:0;border-top:5px solid #c9a24a}}
.head{{position:absolute;top:62px;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:28px}}.head img{{width:200px}}.head div{{font-size:46px;font-weight:800;color:#b3151b}}
#c{{position:absolute;top:220px;left:40px;right:40px;bottom:110px;overflow:hidden;column-count:2;column-gap:36px;column-fill:auto}}
.r{{break-inside:avoid;margin-bottom:.7em;padding-bottom:.5em;border-bottom:2px solid rgba(201,162,74,.5)}}
h2{{font-size:1.25em;font-weight:800;color:#b3151b;line-height:1.15}}.meta{{color:#8a5a2e;font-weight:600;font-size:.9em}}
h3{{font-size:.85em;color:#b07a42;text-transform:uppercase;letter-spacing:.1em;margin:.45em 0 .1em}}
ul,ol{{padding-left:1.1em}}li{{margin:.05em 0;line-height:1.25}}p{{line-height:1.25}}
.foot{{position:absolute;bottom:52px;width:100%;text-align:center;font-size:30px;font-weight:700;color:#8a5a2e}}.e{{font-family:'Noto Color Emoji'}}"""
blocks=""
for p in parts:
    n,t,meta,b=parse(p)
    blocks+=f"<div class='r'><h2>{n}. {html.escape(t)}</h2>"+(f"<div class='meta'>{html.escape(meta)}</div>" if meta else "")+body_html(b)+"</div>"
FIT="<script>let c=document.getElementById('c');let s=40;const ok=()=>c.scrollWidth<=c.clientWidth+2&&c.scrollHeight<=c.clientHeight+2;c.style.fontSize=s+'px';while(!ok()&&s>14){s-=0.5;c.style.fontSize=s+'px'}document.title=s</script>"
h=f"<!doctype html><html lang='tr'><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='band top'></div><div class='head'><img src='logo.png'><div>ile 5 tarif</div></div><div id='c'>{blocks}</div><div class='foot'>Sipariş için bu sohbete yazabilirsiniz <span class='e'>🤎</span></div><div class='band bot'></div>{FIT}</body></html>"
open('h.html','w').write(h)
js=f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});await p.goto('file://'+process.argv[2]);await p.waitForTimeout(500);console.log('font',await p.title());await p.screenshot({{path:process.argv[3]}});await b.close();}})();"""
open('sh.js','w').write(js)
subprocess.run(["node","sh.js",os.path.abspath('h.html'),os.path.abspath('h.png')],check=True)
Image.open('h.png').convert('RGB').save(out,quality=93)
