"""Zifir - Uzak: procedural 9:16 lyric reels."""
import math, os, re, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SONG = os.path.join(HERE, "uzak.m4a")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
ONLY = sys.argv[2:] if len(sys.argv) > 2 else None
W, H, FPS = 1080, 1920, 30
BW, BH = int(W * 1.08), int(H * 1.08)
F_SERIF = os.path.join(HERE, "fonts", "PlayfairDisplay[wght].ttf")
F_ITAL = os.path.join(HERE, "fonts", "PlayfairDisplay-Italic[wght].ttf")
F_SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"


# ---------- lyrics ----------
def load_lyrics():
    raw = open(os.path.join(HERE, "subs.srt"), encoding="utf-8").read()
    out = []
    for block in raw.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3 or lines[2].startswith("["):
            continue
        a, b = re.findall(r"(\d+):(\d+):(\d+),(\d+)", lines[1])
        ts = [int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000 for h, m, s, ms in (a, b)]
        out.append((ts[0], ts[1], lines[2]))
    # a line lasts until the next one starts, capped at 4.5 s (long tails are instrumental)
    fixed = []
    for i, (s, e, txt) in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else e
        fixed.append((s, min(nxt - 0.25, s + 4.5), txt))
    return fixed


LYRICS = load_lyrics()


# ---------- helpers ----------
def vgrad(h, w, stops):
    ys = np.linspace(0, 1, h)
    cols = np.stack([np.interp(ys, [p for p, _ in stops], [c[i] for _, c in stops]) for i in range(3)], -1)
    return np.repeat(cols[:, None, :], w, axis=1).astype(np.float32)


def glow(img, cx, cy, r, color, k=1.0):
    h, w = img.shape[:2]
    x0, x1 = max(0, int(cx - 3 * r)), min(w, int(cx + 3 * r))
    y0, y1 = max(0, int(cy - 3 * r)), min(h, int(cy + 3 * r))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r))) * k
    img[y0:y1, x0:x1] += g[..., None] * np.array(color, np.float32)


def blur(img, s):
    return cv2.GaussianBlur(img, (0, 0), s)


class Particles:
    def __init__(self, n, seed, area, vel, size, color, alpha, wobble=20, glow_r=0):
        r = np.random.default_rng(seed)
        x0, y0, x1, y1 = area
        self.area = area
        self.p = np.stack([r.uniform(x0, x1, n), r.uniform(y0, y1, n)], 1)
        self.v = np.stack([r.uniform(*vel[0], n), r.uniform(*vel[1], n)], 1)
        self.s = r.uniform(*size, n)
        self.ph = r.uniform(0, 6.28, n)
        self.a = r.uniform(*alpha, n)
        self.color, self.wob, self.glow_r = np.array(color, np.float32), wobble, glow_r

    def draw(self, img, t):
        x0, y0, x1, y1 = self.area
        pos = self.p + self.v * t
        pos[:, 0] += np.sin(t * 0.7 + self.ph) * self.wob
        pos[:, 0] = x0 + (pos[:, 0] - x0) % (x1 - x0)
        pos[:, 1] = y0 + (pos[:, 1] - y0) % (y1 - y0)
        layer = np.zeros_like(img)
        for (x, y), s, a, ph in zip(pos, self.s, self.a, self.ph):
            tw = 0.65 + 0.35 * math.sin(t * 2.1 + ph * 3)
            cv2.circle(layer, (int(x * 4), int(y * 4)), max(1, int(s * 4)), (a * tw,) * 3, -1, cv2.LINE_AA, 2)
        m = layer[..., :1]
        if self.glow_r:
            m = m + blur(layer, self.glow_r)[..., :1] * 1.5
        img += m * self.color / 255.0 * 255.0


# ---------- scenes (all drawn in base coords BW x BH) ----------
class Sunset:
    def __init__(self, palette="warm", figure=True, stream=False):
        self.hy = int(BH * 0.6)
        if palette == "warm":
            sky = [(0, (12, 12, 38)), (0.3, (45, 28, 78)), (0.48, (140, 62, 92)), (0.57, (245, 140, 78)), (0.6, (255, 190, 120))]
            sea = [(0, (120, 60, 70)), (0.15, (55, 30, 55)), (1, (8, 8, 20))]
            self.sun = (255, 205, 150)
        else:  # lilac dusk
            sky = [(0, (8, 10, 30)), (0.3, (30, 32, 80)), (0.5, (110, 80, 140)), (0.58, (230, 150, 150)), (0.6, (255, 205, 170))]
            sea = [(0, (110, 80, 120)), (0.15, (40, 32, 70)), (1, (6, 8, 22))]
            self.sun = (255, 220, 190)
        top = vgrad(self.hy, BW, [(p / 0.6, c) for p, c in sky])
        bot = vgrad(BH - self.hy, BW, sea)
        img = np.concatenate([top, bot], 0)
        cx, self.cx = BW // 2, BW // 2
        glow(img, cx, self.hy, 520, (120, 60, 30), 1.0)
        glow(img, cx, self.hy, 180, (160, 90, 40), 1.0)
        sun = np.zeros_like(img)
        cv2.circle(sun, (cx, self.hy - 30), 95, self.sun, -1, cv2.LINE_AA)
        sun[self.hy:] = 0
        img = np.maximum(img, blur(sun, 2))
        # clouds: soft horizontal streaks
        rng = np.random.default_rng(3)
        cl = np.zeros_like(img)
        for _ in range(14):
            y = rng.uniform(0.3, 0.55) * BH
            x = rng.uniform(0, BW)
            cv2.ellipse(cl, (int(x), int(y)), (int(rng.uniform(150, 420)), int(rng.uniform(6, 18))), 0, 0, 360, (1, 1, 1), -1, cv2.LINE_AA)
        cl = blur(cl, 10)
        img = img * (1 - 0.35 * cl) + cl * 0.35 * np.array((70, 40, 60), np.float32)
        if figure:
            fg = np.zeros((BH, BW), np.float32)
            rk = np.array([[0, BH], [0, int(BH * .86)], [180, int(BH * .83)], [420, int(BH * .8)], [640, int(BH * .805)],
                           [820, int(BH * .84)], [BW, int(BH * .88)], [BW, BH]], np.int32)
            cv2.fillPoly(fg, [rk], 1, cv2.LINE_AA)
            fx, fy = 520, int(BH * .8)
            body = np.array([[fx - 70, fy + 5], [fx - 78, fy - 70], [fx - 74, fy - 118], [fx - 50, fy - 140],
                             [fx + 50, fy - 140], [fx + 74, fy - 118], [fx + 78, fy - 70], [fx + 70, fy + 5]], np.int32)
            cv2.fillPoly(fg, [body], 1, cv2.LINE_AA)                                          # back + shoulders
            cv2.rectangle(fg, (fx - 15, fy - 175), (fx + 15, fy - 135), 1, -1)                # neck
            cv2.ellipse(fg, (fx, fy - 205), (33, 38), 0, 0, 360, 1, -1, cv2.LINE_AA)          # head
            fg = blur(fg[..., None].repeat(3, 2), 1.2)
            img = img * (1 - fg) + fg * np.array((10, 8, 16), np.float32)
        self.base = img
        self.stream = Particles(160, 9, (BW * .25, BH * .45, BW * .75, BH * .95), ((-15, 15), (-90, -40)),
                                (1.5, 4), (255, 225, 190), (.4, 1), 40, 4) if stream else \
            Particles(50, 9, (0, BH * .2, BW, BH), ((-8, 8), (-20, -8)), (1, 3), (255, 220, 180), (.2, .6), 30, 3)

    def anim(self, f, t):
        rng = np.random.default_rng(int(t * 12))  # shimmer refreshes 12x/s
        layer = np.zeros(f.shape[:2], np.float32)
        for _ in range(110):
            y = self.hy + 6 + abs(rng.normal(0, 1)) * BH * 0.12
            spread = 40 + (y - self.hy) * 0.9
            x = self.cx + rng.normal(0, 1) * spread * 0.45
            ln = rng.uniform(20, 90) * (1 + (y - self.hy) / 300)
            cv2.line(layer, (int(x - ln / 2), int(y)), (int(x + ln / 2), int(y)), rng.uniform(.3, 1), 2, cv2.LINE_AA)
        layer = blur(layer, 1.5)[..., None]
        f += layer * np.array(self.sun, np.float32) * 0.55
        self.stream.draw(f, t)


class Trees:
    def __init__(self):
        hy = 0.7
        img = vgrad(BH, BW, [(0, (14, 14, 42)), (0.35, (60, 38, 88)), (0.55, (190, 92, 90)), (0.66, (255, 160, 95)), (1, (255, 190, 120))])
        glow(img, BW / 2, BH * 0.67, 380, (130, 70, 30))
        S = 2
        sil = Image.new("L", (BW * S, BH * S), 0)
        d = ImageDraw.Draw(sil)
        pts = [(x * S, (BH * hy + 50 * math.sin(x / 260) - 0.00012 * (x - BW / 2) ** 2 * -1) * S) for x in range(0, BW + 10, 10)]
        d.polygon(pts + [(BW * S, BH * S), (0, BH * S)], fill=255)
        rng = np.random.default_rng(11)

        def branch(x, y, ang, ln, wd, depth):
            x2, y2 = x + math.cos(ang) * ln, y - math.sin(ang) * ln
            d.line([(x * S, y * S), (x2 * S, y2 * S)], fill=255, width=max(1, int(wd * S)))
            if depth == 0:
                for _ in range(3):
                    r = rng.uniform(4, 9)
                    ox, oy = rng.normal(0, 8, 2)
                    d.ellipse([(x2 + ox - r) * S, (y2 + oy - r) * S, (x2 + ox + r) * S, (y2 + oy + r) * S], fill=255)
                return
            for s in (-1, 1):
                branch(x2, y2, ang + s * rng.uniform(0.25, 0.5) + rng.normal(0, 0.06), ln * rng.uniform(0.7, 0.8), wd * 0.68, depth - 1)

        K = BH / 2073
        sp = 163 * K * (1.6 if BW > BH else 1)
        for tx, lean in ((BW / 2 - sp, 0.1), (BW / 2 + sp, -0.1)):
            ty = BH * hy + 50 * math.sin(tx / 260) - 12
            branch(tx, ty + 30, math.pi / 2 + lean, 230 * K, 30 * K, 9)
        sil = sil.resize((BW, BH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
        m = np.asarray(sil, np.float32)[..., None] / 255
        self.base = img * (1 - m) + m * np.array((14, 9, 18), np.float32)
        self.leaves = Particles(26, 4, (-50, BH * .1, BW + 50, BH * .9), ((10, 35), (30, 70)), (3, 6), (25, 15, 25), (1, 1), 50)
        self.dust = Particles(45, 5, (0, BH * .3, BW, BH * .8), ((-6, 6), (-15, -5)), (1, 2.5), (255, 220, 170), (.3, .8), 25, 3)

    def anim(self, f, t):
        # leaves are dark: draw as subtraction
        tmp = np.zeros_like(f)
        self.leaves.draw(tmp, t)
        f -= np.minimum(tmp, 1) * f * 0.85
        self.dust.draw(f, t)


class Candle:
    def __init__(self):
        img = vgrad(BH, BW, [(0, (6, 4, 4)), (1, (14, 9, 7))])
        self.cx, self.top = BW / 2, BH * 0.58
        glow(img, self.cx, self.top - 100, 700, (40, 20, 8))
        body = np.zeros_like(img)
        cv2.rectangle(body, (int(self.cx - 85), int(self.top)), (int(self.cx + 85), BH), (1, 1, 1), -1)
        cv2.ellipse(body, (int(self.cx), int(self.top)), (85, 18), 0, 0, 360, (1, 1, 1), -1, cv2.LINE_AA)
        body = blur(body, 1.5)
        yy = np.linspace(0, 1, BH)[:, None, None]
        shade = np.clip(1.2 - (yy - self.top / BH) * 2.2, 0.15, 1.2)
        xx = (np.arange(BW)[None, :, None] - self.cx) / 85
        shade = shade * np.clip(1 - 0.5 * xx ** 2, 0.2, 1)
        img = img * (1 - body) + body * np.array((205, 170, 130), np.float32) * shade
        cv2.line(img, (int(self.cx), int(self.top)), (int(self.cx + 2), int(self.top - 28)), (20, 15, 15), 4, cv2.LINE_AA)
        self.base = img
        self.dust = Particles(40, 7, (0, 0, BW, BH), ((-5, 5), (-12, -4)), (1, 2.5), (255, 190, 120), (.2, .7), 30, 3)

    def anim(self, f, t):
        n = math.sin(t * 7.3) * 0.5 + math.sin(t * 13.1 + 1) * 0.3 + math.sin(t * 3.1) * 0.2
        fl = 1 + 0.07 * n
        sway = 6 * math.sin(t * 2.3) + 3 * math.sin(t * 5.7)
        glow(f, self.cx, self.top - 120, 650, (55, 28, 8), fl)
        glow(f, self.cx, self.top - 110, 200, (90, 50, 15), fl)
        hgt, wid = 230 * fl, 46
        x0, x1 = int(self.cx - 120), int(self.cx + 120)
        y0, y1 = int(self.top - 330), int(self.top - 10)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        base_y = self.top - 30
        v = np.clip((base_y - yy) / hgt, -0.3, 1.5)  # 0 at wick, 1 at tip
        prof = wid * np.clip(np.sin(np.pi * np.clip(v + 0.12, 0, 1) ** 0.55), 0.02, 1) * np.clip(1 - v, 0, 1) ** 0.35
        dx = (xx - self.cx - sway * np.clip(v, 0, 1) ** 2) / (prof + 1e-3)
        body = np.exp(-dx ** 2 * 1.6) * (v > -0.12) * np.clip((1 - v) * 3, 0, 1) * np.clip((v + 0.15) * 5, 0, 1)
        core = np.exp(-dx ** 2 * 4) * np.clip(1 - v * 1.7, 0, 1) * np.clip((v + 0.05) * 6, 0, 1)
        blue = np.exp(-dx ** 2 * 2) * np.exp(-((v - 0.02) / 0.06) ** 2) * 0.5
        reg = f[y0:y1, x0:x1]
        reg += body[..., None] * np.array((255, 130, 35), np.float32)
        reg += core[..., None] * np.array((255, 235, 190), np.float32)
        reg += blue[..., None] * np.array((60, 90, 255), np.float32)
        self.dust.draw(f, t)


class Rain:
    def __init__(self, warm=False, seed=1):
        rng = np.random.default_rng(seed)
        img = vgrad(BH, BW, [(0, (6, 9, 18)), (0.6, (14, 18, 34)), (1, (8, 10, 20))])
        bok = np.zeros_like(img)
        cols = [(255, 170, 80), (255, 120, 70), (120, 170, 255), (255, 230, 200), (255, 80, 90)] if warm else \
               [(120, 170, 255), (90, 130, 230), (255, 190, 120), (200, 220, 255), (255, 140, 90)]
        for _ in range(55):
            c = np.array(cols[rng.integers(len(cols))], np.float32) * rng.uniform(.12, .45)
            cv2.circle(bok, (int(rng.uniform(0, BW)), int(rng.normal(.62, .13) * BH)), int(rng.uniform(40, 120)),
                       c.tolist(), -1, cv2.LINE_AA)
        img = img + blur(bok, 30)
        glow(img, BW * .5, BH * .62, 600, (25, 22, 30))
        # static droplets: slightly brighter lens + highlight
        dl = np.zeros_like(img)
        hl = np.zeros(img.shape[:2], np.float32)
        for _ in range(380):
            x, y, r = int(rng.uniform(0, BW)), int(rng.uniform(0, BH)), rng.uniform(4, 13)
            cv2.circle(dl, (x, y), int(r), (1, 1, 1), -1, cv2.LINE_AA)
            cv2.circle(hl, (int(x - r * .3), int(y - r * .35)), max(1, int(r * .25)), 1, -1, cv2.LINE_AA)
        dl = blur(dl, .8)
        img = img * (1 - dl * .8) + dl * .8 * (blur(img, 40) * 1.6 + 8)
        img += blur(hl, 1.2)[..., None] * 18
        self.base = img
        self.blurred = blur(img, 25) * 1.9 + 12
        self.drops = [(rng.uniform(0, BW), rng.uniform(0, BH), rng.uniform(120, 300), rng.uniform(9, 15), rng.uniform(0, 6.28))
                      for _ in range(9)]

    def anim(self, f, t):
        mask = np.zeros(f.shape[:2], np.float32)
        hl = np.zeros_like(mask)
        for x, y0, sp, r, ph in self.drops:
            y = (y0 + sp * t) % (BH + 400) - 200
            xx = x + 6 * math.sin(y / 90 + ph)
            for k in range(1, 12):
                ty = y - k * r * 2.2
                cv2.circle(mask, (int(x + 6 * math.sin(ty / 90 + ph)), int(ty)), max(1, int(r * .45 * (1 - k / 13))), .6, -1, cv2.LINE_AA)
            cv2.circle(mask, (int(xx), int(y)), int(r), 1, -1, cv2.LINE_AA)
            cv2.circle(hl, (int(xx - r * .3), int(y - r * .35)), max(1, int(r * .3)), 1, -1, cv2.LINE_AA)
        m = blur(mask, .8)[..., None]
        f[:] = f * (1 - m * .9) + m * .9 * self.blurred
        f += blur(hl, 1)[..., None] * 40


class Night:
    def __init__(self):
        rng = np.random.default_rng(21)
        self.hy = int(BH * 0.68)
        img = np.concatenate([vgrad(self.hy, BW, [(0, (3, 5, 14)), (0.7, (10, 16, 40)), (1, (24, 34, 66))]),
                              vgrad(BH - self.hy, BW, [(0, (14, 20, 40)), (1, (3, 5, 12))])], 0)
        self.mx, self.my = BW * 0.7, BH * 0.43
        glow(img, self.mx, self.my, 420, (22, 28, 45))
        glow(img, self.mx, self.my, 140, (40, 44, 55))
        moon = np.zeros_like(img)
        cv2.circle(moon, (int(self.mx), int(self.my)), 70, (235, 230, 215), -1, cv2.LINE_AA)
        cut = np.zeros(img.shape[:2], np.float32)
        cv2.circle(cut, (int(self.mx + 34), int(self.my - 18)), 66, 1, -1, cv2.LINE_AA)
        moon *= (1 - blur(cut, 2))[..., None]
        img = np.maximum(img, blur(moon, 1.2))
        self.stars = [(rng.uniform(0, BW), rng.uniform(0, self.hy - 20) ** 1 * rng.uniform(.4, 1), rng.uniform(.6, 2.2),
                       rng.uniform(.2, 1), rng.uniform(0, 6.28), rng.uniform(.5, 2.5)) for _ in range(380)]
        self.base = img

    def anim(self, f, t):
        layer = np.zeros(f.shape[:2], np.float32)
        for x, y, s, b, ph, sp in self.stars:
            cv2.circle(layer, (int(x * 4), int(y * 4)), int(s * 4), b * (0.55 + 0.45 * math.sin(t * sp + ph)), -1, cv2.LINE_AA, 2)
        f += (layer + blur(layer, 3) * 2)[..., None] * np.array((220, 225, 255), np.float32)
        rng = np.random.default_rng(int(t * 10))
        sh = np.zeros_like(layer)
        for _ in range(70):
            y = self.hy + 8 + abs(rng.normal(0, 1)) * BH * 0.14
            x = self.mx + rng.normal(0, 1) * (25 + (y - self.hy) * 0.35)
            ln = rng.uniform(15, 70)
            cv2.line(sh, (int(x - ln / 2), int(y)), (int(x + ln / 2), int(y)), rng.uniform(.3, 1), 2, cv2.LINE_AA)
        f += blur(sh, 1.3)[..., None] * np.array((200, 200, 190), np.float32) * 0.6


class Heart:
    def __init__(self):
        img = vgrad(BH, BW, [(0, (5, 2, 4)), (1, (8, 3, 5))])
        glow(img, BW / 2, BH * .43, 800, (30, 6, 10))
        th = np.linspace(0, 2 * np.pi, 400)
        s = 15 if BH > BW else 10.5
        xs = BW / 2 + s * 16 * np.sin(th) ** 3
        ys = BH * .43 - s * (13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th))
        m = np.zeros((BH, BW), np.float32)
        cv2.fillPoly(m, [np.stack([xs, ys], 1).astype(np.int32)], 1, cv2.LINE_AA)
        inner = blur(m, 30) * m
        self.core = blur(m, 2)[..., None] * np.array((200, 25, 45), np.float32) + inner[..., None] * np.array((80, 60, 60), np.float32)
        self.g1 = blur(m, 35)[..., None] * np.array((150, 20, 35), np.float32)
        self.g2 = blur(m, 140)[..., None] * np.array((110, 15, 25), np.float32)
        self.base = img
        self.embers = Particles(70, 12, (BW * .15, 0, BW * .85, BH), ((-10, 10), (-80, -30)), (1.5, 3.5), (255, 110, 70), (.3, 1), 35, 4)

    def anim(self, f, t):
        ph = (t % 1.25) / 1.25  # lub-dub
        beat = math.exp(-((ph - .05) / .05) ** 2) + .6 * math.exp(-((ph - .25) / .05) ** 2)
        f += self.core * (0.85 + 0.25 * beat) + self.g1 * (0.6 + 0.6 * beat) + self.g2 * (0.7 + 0.5 * beat)
        self.embers.draw(f, t)


# ---------- text ----------
def font(path, size, wght=None):
    fnt = ImageFont.truetype(path, size)
    if wght:
        try:
            fnt.set_variation_by_axes([wght])
        except Exception:
            pass
    return fnt


def text_layer(text, fnt, maxw, align_y, spacing=1.18, tracking=0):
    """Return RGBA float layer (H,W,4) with centered wrapped text + soft shadow."""
    words, lines, cur = text.split(), [], ""
    dummy = ImageDraw.Draw(Image.new("L", (1, 1)))
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if dummy.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    lh = fnt.size * spacing
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    y = align_y - lh * len(lines) / 2
    for ln in lines:
        d.text((W / 2, y + lh / 2), ln, font=fnt, fill=255, anchor="mm")
        y += lh
    a = np.asarray(img, np.float32) / 255
    sh = np.asarray(img.filter(ImageFilter.GaussianBlur(8)), np.float32) / 255
    sh2 = np.asarray(img.filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
    sh = np.clip(sh * 0.9 + np.clip(sh2 * 3.5, 0, 1) * 0.6, 0, 1)
    return a, sh


def comp_text(frame, layer, alpha, color=(255, 255, 255), dy=0):
    a, sh = layer
    if alpha <= 0:
        return
    if dy:
        a, sh = np.roll(a, dy, 0), np.roll(sh, dy, 0)
    frame *= (1 - sh[..., None] * 0.8 * alpha)
    frame[:] = frame * (1 - a[..., None] * alpha) + a[..., None] * alpha * np.array(color, np.float32)


# ---------- reels ----------
# (ad, sahne, ayar, kapaktaki şarkı sözü, başlangıç, bitiş). Videoda ek yazı yok; söz yalnızca kapakta.
REELS = [
    ("01-anlatan", Rain, {}, "Oysa seni sana anlatan ben idim", 58.6, 73.4),
    ("02-yok-isem", Rain, {"warm": True, "seed": 5}, "Ben eğer yok isem sen olmazsın dedim", 138.2, 152.6),
    ("03-kalp", Heart, {}, "Elindeki kalbi yerine koysana", 8.6, 24.4),
    ("04-agaclar", Trees, {}, "Yan yana ağacız gölge yeter bize", 62.4, 76.0),
    ("05-ufuk", Night, {}, "Ufuk daldırır beni senli bir hayale", 123.1, 138.6),
    ("06-alev", Candle, {}, "Alevin içinde yanması ayrı zevk", 24.1, 39.5),
    ("07-vardim", Sunset, {}, "Vardım kendime ufka bakmam hiç sakın", 35.2, 50.9),
    ("08-ardinda", Sunset, {"palette": "lilac", "figure": False, "stream": True},
     "Ardında ne parçam ne de ben varım", 47.1, 62.6),
]


def render(name, scene_cls, kw, hook, t0, t1):
    os.makedirs(OUT, exist_ok=True)
    scene = scene_cls(**kw)
    dur = t1 - t0
    n = int(dur * FPS)
    tag_l = text_layer("ZİFİR  —  UZAK", font(F_SANS, 30), 900, H * 0.715)
    lyr = [(s - t0, e - t0, text_layer(txt, font(F_SERIF, 58, 500), 900, H * 0.6)) for s, e, txt in LYRICS
           if e > t0 and s < t1]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = np.clip(1.25 - 0.75 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2), 0.35, 1)[..., None]
    rng = np.random.default_rng(0)
    grains = [rng.normal(0, 7, (H, W, 1)).astype(np.float32) for _ in range(6)]
    mp4 = os.path.join(OUT, f"{name}.mp4")
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-ss", f"{t0}", "-t", f"{dur}", "-i", SONG, "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:d=0.25,afade=t=out:st={dur - 0.9}:d=0.9",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", mp4], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        f = scene.base.copy()
        scene.anim(f, t)
        z = 1.0 + 0.07 * (t / dur)  # slow push-in
        cw, ch = BW / z / 1.08 * 1.08, BH / z
        cw = BW / z
        x0, y0 = (BW - cw) / 2, (BH - ch) / 2
        M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        fr = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR)
        fr = np.clip(fr, 0, 255) * vign + grains[i % 6]
        fr = np.clip(fr, 0, 255)
        fade_all = min(1, t / 0.35)
        comp_text(fr, tag_l, 0.8, (235, 225, 215))
        for s, e, L in lyr:
            if s - 0.05 <= t <= e:
                a = min(1, (t - s + 0.05) / 0.25, (e - t) / 0.2)
                rise = int(14 * (1 - min(1, (t - s + 0.05) / 0.4)))
                comp_text(fr, L, max(0, a), (255, 246, 235), rise)
        if fade_all < 1:
            fr *= 0.3 + 0.7 * fade_all
        if i == int(FPS * 1.5):
            Image.fromarray(fr.astype(np.uint8)).save(os.path.join(OUT, f"{name}-kapak.jpg"), quality=92)
        ff.stdin.write(fr.astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()
    print("done", mp4, flush=True)


if __name__ == "__main__":
    for r in REELS:
        if ONLY is None or r[0] in ONLY:
            render(*r)
