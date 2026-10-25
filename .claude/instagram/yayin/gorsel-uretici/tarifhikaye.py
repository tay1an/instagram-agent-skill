import re, json, subprocess, os, sys, html
from PIL import Image
OUT="/home/user/instagram-agent-skill/.claude/instagram/gorseller"
src=open('/home/user/instagram-agent-skill/.claude/instagram/tarif-listesi.md').read().split('---',1)[1].rsplit('\n---\n',1)[0]
parts=re.split(r'\n(?=\*\*\d\. )',('**1. '+src.split('**1. ',1)[1]).strip())
def parse(p):
    p=re.sub(r'\n +',' ',p)
    lines=p.splitlines(); title=lines[0].replace('**','')
    m=re.match(r'(\d)\. (.*?)(?: \((.*)\))?$',title); return m.group(1),m.group(2),m.group(3),"\n".join(lines[1:]).strip()
def body_html(b):
    out=[]
    for blk in b.split('\n\n'):
        ls=blk.strip().splitlines()
        if not ls: continue
        if ls[0].endswith(':'):
            out.append(f'<h3>{html.escape(ls[0][:-1])}</h3>'); ls=ls[1:]
        if ls and ls[0].startswith('- '):
            out.append('<ul>'+''.join(f'<li>{html.escape(l[2:])}</li>' for l in ls)+'</ul>')
        elif ls and re.match(r'\d\.',ls[0]):
            out.append('<ol>'+''.join(f'<li>{html.escape(re.sub(r"^\d\. ","",l))}</li>' for l in ls)+'</ol>')
        elif ls: out.append('<p>'+html.escape(' '.join(ls))+'</p>')
    return ''.join(out)
CSS="""*{margin:0;padding:0;box-sizing:border-box}body{width:1080px;height:1920px;overflow:hidden;font-family:'Inter',sans-serif;background:radial-gradient(ellipse at 50% 45%,#fffaf0 0%,#f6ead4 65%,#ead6b4 100%);color:#4a2510;position:relative}
.band{position:absolute;left:0;right:0;height:120px;background:#b3151b}.top{top:0;border-bottom:6px solid #c9a24a}.bot{bottom:0;border-top:6px solid #c9a24a}
.logo{position:absolute;top:160px;left:50%;transform:translateX(-50%);width:300px}
#c{position:absolute;top:400px;left:80px;right:80px;bottom:260px;overflow:hidden}
.no{font-family:'Inter Display';font-weight:900;color:#c9a24a;font-size:1.6em;line-height:1}
h2{font-size:1.45em;font-weight:800;color:#b3151b;line-height:1.15;margin:.1em 0 .15em}
.meta{color:#8a5a2e;font-weight:600;margin-bottom:.5em}
h3{font-size:1.02em;color:#b07a42;text-transform:uppercase;letter-spacing:.12em;margin:.8em 0 .25em}
ul,ol{padding-left:1.15em}li{margin:.12em 0;line-height:1.32}p{line-height:1.35;margin:.4em 0}
.foot{position:absolute;bottom:160px;width:100%;text-align:center;font-size:34px;font-weight:600;color:#8a5a2e}
.e{font-family:'Noto Color Emoji'}
.cover{position:absolute;top:420px;left:80px;right:80px;bottom:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:34px}
"""
FIT="<script>let c=document.getElementById('c');let s=46;c.style.fontSize=s+'px';while(c.scrollHeight>c.clientHeight&&s>24){s--;c.style.fontSize=s+'px'}document.title=s</script>"
def page(inner,fit=True): return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='band top'></div><img class='logo' src='logo.png'>{inner}<div class='foot'>Sipariş için WhatsApp'tan yazabilirsiniz <span class='e'>🤎</span></div><div class='band bot'></div>{FIT if fit else ''}</body></html>"
frames=[("tarif-0-kapak",page("<div class='cover'><div style='font-size:44px;font-weight:600;letter-spacing:8px;color:#b07a42'>ÖNE ÇIKAN</div><div style='font-size:120px;font-weight:900;color:#b3151b;line-height:1'>Tarifler</div><div style='font-size:56px;font-weight:700'>Aziz Tahin ile<br>5 tarif</div><div style='font-size:42px;color:#6b3a1c'>Kaydırın, kaydedin <span class='e'>🥄</span></div></div>",False))]
for p in parts:
    n,t,meta,b=parse(p)
    head=f"<div class='no'>{n}</div><h2>{html.escape(t)}</h2>"+(f"<div class='meta'>{html.escape(meta)}</div>" if meta else "")
    if n=='1':
        a,y=b.split('\nYapılışı:',1)
        frames.append((f"tarif-{n}a",page(f"<div id='c'>{head}{body_html(a)}</div>")))
        frames.append((f"tarif-{n}b",page(f"<div id='c'>{head.replace('</h2>',' <span style=\"font-size:.6em;color:#8a5a2e\">(devamı)</span></h2>')}{body_html('Yapılışı:'+y)}</div>")))
    else:
        frames.append((f"tarif-{n}",page(f"<div id='c'>{head}{body_html(b)}</div>")))
ids=[]
for name,h in frames:
    open('t.html','w').write(h)
    subprocess.run(["node","shot.js",os.path.abspath('t.html'),os.path.abspath(name+'.png')],check=True)
    Image.open(name+'.png').convert('RGB').save(f"{OUT}/hikaye-{name}.jpg",quality=92); ids.append(name)
print(ids)
ims=[Image.open(f"{OUT}/hikaye-{i}.jpg").resize((270,480)) for i in ids]
c=Image.new('RGB',(len(ims)*280,480),'white')
for k,im in enumerate(ims): c.paste(im,(k*280,0))
c.save('tarif-onizleme.jpg')
