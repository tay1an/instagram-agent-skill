"""Gerçek görüntüyle açılan Aziz Tahin reel'i üretir.
Kullanım: python3 reel.py SPEC.json [--taslak]
SPEC: {"id": "...", "jingle": 1|2, "sahneler": [...]}
sahne türleri:
  {"tip":"video","src":"medya/video/x.mp4","bas":0,"sure":3.2,"ust":"KÜÇÜK","baslik":"HTML"}
  {"tip":"foto","src":"medya/x.jpg","pos":"50% 60%","sure":2.4,"num":"1","baslik":"HTML"}
  {"tip":"son","baslik":"HTML","alt":"HTML","sure":3.4}
Yollar .claude/instagram/ altına göredir. Çıktı: medya/reel-<id>.mp4
"""
import json, os, shutil, subprocess, sys
KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HF = os.path.join(KOK, "hyperframes")
spec = json.load(open(sys.argv[1])); taslak = "--taslak" in sys.argv
rid = spec["id"]; D = os.path.join(HF, rid); A = os.path.join(D, "assets")
os.makedirs(A, exist_ok=True)
for x in ("fonts", "vendor", "hyperframes.json", "package.json"):
    s = os.path.join(HF, "kis-kasigi", x); d = os.path.join(D, x)
    if not os.path.exists(d): (shutil.copytree if os.path.isdir(s) else shutil.copy)(s, d)
open(os.path.join(D, "meta.json"), "w").write(json.dumps({"id": rid, "name": rid}))
shutil.copy(os.path.join(HF, "kis-kasigi", "assets", "kavanoz.mp4"), os.path.join(A, "kavanoz.mp4"))
scenes, videos, anim, t = [], [], [], 0.0
dur = sum(s["sure"] for s in spec["sahneler"])
for i, s in enumerate(spec["sahneler"], 1):
    a, b = round(t, 2), round(t + s["sure"], 2)
    if s["tip"] == "video":
        out = os.path.join(A, f"v{i}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s.get("bas", 0)), "-t", str(s["sure"] + 0.1), "-i", os.path.join(KOK, s["src"]),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30" + (",setpts=PTS/%s" % s["hiz"] if s.get("hiz") else ""),
            "-an", "-c:v", "libx264", "-crf", "18", "-g", "15", "-pix_fmt", "yuv420p", out], check=True)
        videos.append(f'<video id="v{i}" class="clip" src="assets/v{i}.mp4" muted playsinline data-start="{a}" data-duration="{s["sure"]}" data-track-index="2" style="z-index: 2; position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover"></video>')
        scenes.append(f'''<div id="s{i}" class="scene clip" data-start="{a}" data-duration="{s["sure"]}" data-track-index="1" style="z-index: 3"><div class="bant"></div>
        <div class="safe"><div class="kicker" id="k{i}">{s.get("ust","")}</div><h1 class="big" id="t{i}" style="margin-top: 22px; font-size: {s.get("boy",112)}px">{s["baslik"]}</h1></div></div>''')
        anim += [f'tl.fromTo("#k{i}", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, {a});',
                 f'tl.fromTo("#t{i}", {{ opacity: 0, scale: 0.85, transformOrigin: "left center" }}, {{ opacity: 1, scale: 1, ease: "back.out(1.7)", duration: 0.45 }}, {a + 0.1});']
    elif s["tip"] == "foto":
        ext = os.path.splitext(s["src"])[1]; shutil.copy(os.path.join(KOK, s["src"]), os.path.join(A, f"p{i}{ext}"))
        num = f'<div class="num" id="n{i}">{s["num"]}</div>' if s.get("num") else ""
        scenes.append(f'''<div id="s{i}" class="scene clip" data-start="{a}" data-duration="{s["sure"]}" data-track-index="1">
        <div class="photo" id="p{i}" style="inset: 0; background-image: url('assets/p{i}{ext}'); background-position: {s.get("pos","50% 50%")}"></div><div class="bant"></div>
        <div class="safe">{num}<div class="lbl" id="l{i}" style="font-size: {s.get("boy",92)}px">{s["baslik"]}</div></div></div>''')
        anim += [f'tl.fromTo("#p{i}", {{ scale: 1.18 }}, {{ scale: 1.02, duration: {s["sure"]}, ease: "power1.out" }}, {a});',
                 f'tl.fromTo("#l{i}", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {a + 0.2});']
        if num: anim.append(f'tl.fromTo("#n{i}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }}, {a + 0.05});')
    else:
        videos.append(f'<video id="vk" class="clip" src="assets/kavanoz.mp4" muted playsinline data-start="{a}" data-duration="{min(3.37, s["sure"])}" data-track-index="2" style="z-index: 6; position: absolute; left: 0; top: 590px; width: 1080px; height: 608px; object-fit: cover"></video>')
        scenes.append(f'''<div id="s{i}" class="scene clip" data-start="{a}" data-duration="{s["sure"]}" data-track-index="1" style="background: var(--krem); z-index: 5">
        <div class="safe" style="top: 250px"><div id="c1" style="font-weight: 900; font-size: {s.get("boy",92)}px; line-height: 0.95; color: var(--kirmizi); letter-spacing: -3px">{s["baslik"]}</div>
        <div id="c2" style="font-weight: 700; font-size: 42px; line-height: 1.3; margin-top: 18px; color: var(--kahve)">{s.get("alt","")}</div></div>
        <div class="safe" style="top: 1230px"><div id="c3"><span class="pill" style="background: var(--kahve); color: var(--krem); font-size: 60px; line-height: 1.12; padding: 26px 34px">SİPARİŞ İÇİN<br />DM'DEN YAZIN</span></div>
        <div id="c4" style="margin-top: 28px; font-weight: 700; font-size: 44px; color: var(--kahve)">Türkiye'nin her iline gönderim<br /><span style="color: var(--kirmizi)">@aziz.tahin</span></div></div></div>''')
        anim += [f'tl.fromTo("#c1", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, ease: "back.out(1.7)", duration: 0.45 }}, {a + 0.05});',
                 f'tl.fromTo("#c2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {a + 0.3});',
                 f'tl.fromTo("#vk", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {a});',
                 f'tl.fromTo("#c3", {{ opacity: 0, scale: 0.8, transformOrigin: "left center" }}, {{ opacity: 1, scale: 1, ease: "back.out(1.7)", duration: 0.45 }}, {a + 0.6});',
                 f'tl.to("#c3", {{ scale: 1.05, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {a + 1.3});',
                 f'tl.fromTo("#c4", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {a + 0.9});']
    anim.insert(0, f'if ({a} > 0) {{ tl.set("#s{i}", {{ autoAlpha: 0 }}, 0); tl.set("#s{i}", {{ autoAlpha: 1 }}, {a}); }} ' + (f'tl.set("#s{i}", {{ autoAlpha: 0 }}, {b});' if b < dur - 0.01 else ""))
    t = b
src = open(os.path.join(HF, "kis-kasigi", "index.html")).read()
head = src[:src.index("<body>")].replace("Kış sabahı kaşığı", spec.get("baslik", rid))
html = head + f'''<body>
    <div id="root" data-composition-id="{rid}" data-width="1080" data-height="1920" data-start="0" data-duration="{round(dur,2)}">
      {chr(10).join(scenes)}
      {chr(10).join(videos)}
      <script>
        (function () {{
          const tl = gsap.timeline({{ paused: true }});
          {chr(10).join(anim)}
          window.__timelines = window.__timelines || {{}};
          window.__timelines["{rid}"] = tl;
        }})();
      </script>
    </div>
  </body>
</html>
'''
open(os.path.join(D, "index.html"), "w").write(html)
S = os.environ.get("SCRATCH", "/tmp")
sessiz = os.path.join(S, f"{rid}-sessiz.mp4")
cmd = ["npx", "--yes", "hyperframes@0.8.209", "render", "-o", sessiz] + (["-f", "3", "-q", "draft"] if taslak else [])
r = subprocess.run(cmd, cwd=D, capture_output=True, text=True)
print([l for l in r.stdout.splitlines() if "rendered" in l] or r.stdout[-800:] + r.stderr[-800:])
for x in (".hyperframes", ".transcode-cache"): shutil.rmtree(os.path.join(D, x), ignore_errors=True)
if not taslak:
    out = os.path.join(KOK, "medya", f"reel-{rid}.mp4")
    subprocess.run(["bash", os.path.join(KOK, "yayin", "jingle-ekle.sh"), sessiz, out, str(spec["jingle"]), "0"], check=True)
    print(out)
