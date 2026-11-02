"""Klip motoru: kamera, kenar yumuşatmalı çizim, parlama katmanı, çöp adam, nesneler."""
import math
import numpy as np
import cv2

W, H = 1920, 1080
SH = 4               # cv2 alt piksel kaydırması
K = 1 << SH

KREM = (238, 230, 218)
KIRMIZI = (235, 64, 70)
SICAK = (255, 178, 92)
AY = (246, 240, 222)
GOK_UST = (8, 11, 26)
GOK_ALT = (28, 27, 52)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def bol(t, a, b):
    """t'nin [a,b] aralığındaki yeri, 0-1 kırpılmış."""
    return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= b)


def renk_kar(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def gok(ust=GOK_UST, alt=GOK_ALT):
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.array(ust, np.float32) * (1 - y) + np.array(alt, np.float32) * y
    return np.repeat(g, W, 1).astype(np.uint8)


class Tuval:
    def __init__(self, zemin, cx=W / 2, cy=H / 2, z=1.0):
        self.img = zemin.copy()
        self.glow = np.zeros((H // 4, W // 4, 3), np.float32)
        self.cx, self.cy, self.z = cx, cy, z

    def p(self, x, y):
        return (int(((x - self.cx) * self.z + W / 2) * K), int(((y - self.cy) * self.z + H / 2) * K))

    def s(self, v):
        return max(1, int(round(v * self.z)))

    def cizgi(self, a, b, renk=KREM, k=4, alfa=1.0):
        if alfa >= 0.999:
            cv2.line(self.img, self.p(*a), self.p(*b), renk, self.s(k), cv2.LINE_AA, SH)
        else:
            ov = self.img.copy()
            cv2.line(ov, self.p(*a), self.p(*b), renk, self.s(k), cv2.LINE_AA, SH)
            cv2.addWeighted(ov, alfa, self.img, 1 - alfa, 0, self.img)

    def yol(self, pts, renk=KREM, k=4, kapali=False):
        if len(pts) < 2:
            return
        arr = np.array([self.p(*q) for q in pts], np.int32).reshape(-1, 1, 2)
        cv2.polylines(self.img, [arr], kapali, renk, self.s(k), cv2.LINE_AA, SH)

    def daire(self, c, r, renk=KREM, k=4, dolu=False):
        cv2.circle(self.img, self.p(*c), max(1, int(r * self.z * K)), renk, -1 if dolu else self.s(k), cv2.LINE_AA, SH)

    def cokgen(self, pts, renk):
        arr = np.array([self.p(*q) for q in pts], np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(self.img, [arr], renk, cv2.LINE_AA, SH)

    def isik(self, c, r, renk=SICAK, guc=1.0):
        """Parlama katmanına yumuşak ışık (çeyrek çözünürlük)."""
        x, y = self.p(*c)
        cv2.circle(self.glow, (int(x / K / 4), int(y / K / 4)), max(1, int(r * self.z / 4)),
                   tuple(v * guc for v in renk), -1, cv2.LINE_AA)

    def bitir(self):
        g = cv2.GaussianBlur(self.glow, (0, 0), 9)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        return np.clip(self.img.astype(np.float32) + g * 0.9, 0, 255).astype(np.uint8)


# ---------- çöp adam ----------
DUZ = dict(egim=0, bas=0, lua=8, lfa=4, rua=-8, rfa=-4, lth=4, lsh=0, rth=-4, rsh=0)


def poz(**k):
    d = dict(DUZ); d.update(k); return d


def poz_kar(a, b, t):
    return {k: lerp(a[k], b[k], t) for k in a}


def yuru(faz, hiz=1.0):
    s = math.sin(faz)
    return poz(lth=26 * s, lsh=max(0, -30 * s) + 6, rth=-26 * s, rsh=max(0, 30 * s) + 6,
               lua=-22 * s, lfa=-30 - 10 * s, rua=22 * s, rfa=-30 + 10 * s, egim=4)


def _uc(o, aci, boy, yon):
    a = math.radians(aci)
    return (o[0] + math.sin(a) * boy * yon, o[1] + math.cos(a) * boy)


def adam(tv, x, zemin_y, p, yon=1, o=1.0, renk=KREM, kiz=False, sac_faz=0.0, kanat=0.0, kanat_cirp=0.0, alfa=1.0):
    """Ayakları zemin_y'de duran çöp adam. Eklem noktalarını döndürür."""
    k = 4.5 * o
    bacak = 112 * o
    # Kalça: bacak açılarına göre yükseklik (ayak yere bassın)
    def bacak_boy(th, sh):
        a1, a2 = math.radians(th), math.radians(th - sh)
        return 56 * o * math.cos(a1) + 56 * o * math.cos(a2)
    kal_y = zemin_y - max(bacak_boy(p["lth"], p["lsh"]), bacak_boy(p["rth"], p["rsh"]))
    kal = (x, kal_y)
    eg = math.radians(p["egim"])
    omuz = (x + math.sin(eg) * 82 * o * yon, kal_y - math.cos(eg) * 82 * o)
    boyun = (x + math.sin(eg) * 94 * o * yon, kal_y - math.cos(eg) * 94 * o)
    bas_m = (boyun[0] + math.sin(eg + math.radians(p["bas"])) * 22 * o * yon,
             boyun[1] - math.cos(eg + math.radians(p["bas"])) * 22 * o)
    c = renk
    if kanat > 0.01:
        kanatlar(tv, omuz, o, kanat, kanat_cirp, yon)
    tv.cizgi(kal, boyun, c, k)
    tv.daire(bas_m, 21 * o, c, k)
    if kiz:  # at kuyruğu saç ve atkı
        sx = bas_m[0] - 18 * o * yon
        sallan = math.sin(sac_faz) * 6 * o
        tv.yol([(sx, bas_m[1] - 6 * o), (sx - 18 * o * yon, bas_m[1] + 10 * o + sallan),
                (sx - 24 * o * yon, bas_m[1] + 32 * o + sallan)], c, k)
        tv.cizgi((boyun[0] - 10 * o * yon, boyun[1] + 4 * o), (boyun[0] + 10 * o * yon, boyun[1] + 4 * o), KIRMIZI, 7 * o)
        tv.yol([(boyun[0] - 8 * o * yon, boyun[1] + 6 * o), (boyun[0] - 22 * o * yon, boyun[1] + 30 * o + sallan)], KIRMIZI, 6 * o)
    el = {}
    for yan, ua, fa in (("l", p["lua"], p["lfa"]), ("r", p["rua"], p["rfa"])):
        dirsek = _uc(omuz, ua, 46 * o, yon)
        el[yan] = _uc(dirsek, ua + fa, 44 * o, yon)
        tv.yol([omuz, dirsek, el[yan]], c, k)
    ayak = {}
    for yan, th, sh in (("l", p["lth"], p["lsh"]), ("r", p["rth"], p["rsh"])):
        diz = _uc(kal, th, 56 * o, yon)
        ayak[yan] = _uc(diz, th - sh, 56 * o, yon)
        tv.yol([kal, diz, ayak[yan]], c, k)
    return dict(bas=bas_m, omuz=omuz, boyun=boyun, kal=kal, el_l=el["l"], el_r=el["r"],
                gogus=(lerp(omuz[0], kal[0], 0.3), lerp(omuz[1], kal[1], 0.3)), goz=(bas_m[0] + 8 * o * yon, bas_m[1] - 2 * o))


def kanatlar(tv, omuz, o, acik, cirp, yon):
    """Sırttan geriye ve yukarı açılan iki tüylü kanat (yakın ve uzak). acik 0-1, cirp -1..1."""
    kok = (omuz[0] - 8 * o * yon, omuz[1] + 10 * o)
    for katman, (kay, renk, kal) in enumerate((((-14, -6), (150, 146, 140), 2.6), ((0, 0), KREM, 3.2))):
        r0 = (kok[0] + kay[0] * o * yon, kok[1] + kay[1] * o)
        uclar = []
        for i in range(6):
            f = i / 5
            aci = math.radians(lerp(8, 85, f) + cirp * 30 - (1 - acik) * 80)
            boy = (230 - 90 * abs(f - 0.3)) * o * acik
            uc = (r0[0] - math.cos(aci) * boy * yon, r0[1] - math.sin(aci) * boy)
            orta = (lerp(r0[0], uc[0], 0.55) - 14 * o * yon * acik, lerp(r0[1], uc[1], 0.55) - 22 * o * acik)
            tv.yol([r0, orta, uc], renk, kal * o)
            uclar.append(uc)
            if katman == 1:
                tv.isik(uc, 10 * o, (200, 190, 170), 0.25 * acik)
        tv.yol(uclar, renk, kal * o)


def kalp(tv, c, r, renk=KIRMIZI, isik=0.6, catlak=0.0, aci=0.0):
    pts = []
    for i in range(48):
        t = i / 48 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        ca, sa = math.cos(aci), math.sin(aci)
        pts.append((c[0] + (x * ca - y * sa) * r / 16, c[1] + (x * sa + y * ca) * r / 16))
    tv.cokgen(pts, renk)
    if isik:
        tv.isik(c, r * 2.2, renk, isik)
    if catlak > 0:
        z = [(c[0], c[1] - r * 0.6), (c[0] - r * 0.2, c[1] - r * 0.2), (c[0] + r * 0.15, c[1] + r * 0.1), (c[0] - r * 0.05, c[1] + r * 0.5)]
        n = max(2, int(len(z) * catlak + 0.999))
        tv.yol(z[:n], (40, 20, 30), max(2, r * 0.12))


def lamba(tv, x, zemin_y, yan=1.0, t=0.0):
    tepe = (x, zemin_y - 430)
    tv.cizgi((x, zemin_y), tepe, (70, 72, 92), 9)
    kol = (x + 90, zemin_y - 440)
    tv.yol([tepe, (x + 30, zemin_y - 455), kol], (70, 72, 92), 8)
    bas = (kol[0] + 6, kol[1] + 18)
    tv.cokgen([(kol[0] - 16, kol[1] + 4), (kol[0] + 28, kol[1] + 4), (kol[0] + 18, kol[1] + 30), (kol[0] - 6, kol[1] + 30)], (90, 40, 40))
    if yan > 0:
        tv.daire((bas[0], bas[1] + 10), 9, (255, 220, 160), dolu=True)
        tv.isik((bas[0], bas[1] + 10), 70, SICAK, 0.9 * yan)
        tv.isik((bas[0], zemin_y), 160, SICAK, 0.18 * yan)
    return kol


def balonlar(tv, baglanti, t, ucus=0.0, renk=(236, 176, 186)):
    for i, (dx, dy, f) in enumerate(((60, -180, 0.0), (20, -120, 1.7))):
        sal = math.sin(t * 1.3 + f) * 10
        b = (baglanti[0] + dx + sal, baglanti[1] + dy - ucus * (900 + i * 120))
        tv.yol([baglanti if ucus < 0.01 else (b[0] - 6, b[1] + 160), (lerp(baglanti[0], b[0], 0.5) + sal, lerp(baglanti[1], b[1], 0.5)), (b[0], b[1] + 30)], (150, 140, 150), 2)
        tv.daire(b, 30, renk, dolu=True)
        tv.daire((b[0] - 9, b[1] - 10), 6, (255, 230, 236), dolu=True)


def yildizlar(tv, t, n=140, tohum=3, yogun=1.0):
    r = np.random.default_rng(tohum)
    xs, ys, fs = r.uniform(-W, 2 * W, n), r.uniform(-H, H * 0.75, n), r.uniform(0, 6.28, n)
    for x, y, f in zip(xs, ys, fs):
        g = (0.55 + 0.45 * math.sin(t * 1.6 + f)) * yogun
        tv.daire((x, y), 1.8, renk_kar((20, 20, 40), (240, 236, 220), g), dolu=True)


def sehir(tv, zemin_y, tohum=1, renk=(18, 20, 38)):
    r = np.random.default_rng(tohum)
    x = -W
    while x < 2 * W:
        w = r.uniform(60, 160); h = r.uniform(80, 300)
        tv.cokgen([(x, zemin_y), (x, zemin_y - h), (x + w, zemin_y - h), (x + w, zemin_y)], renk)
        for _ in range(int(h // 60)):
            if r.random() < 0.35:
                wx, wy = x + r.uniform(10, w - 20), zemin_y - r.uniform(20, h - 20)
                tv.cokgen([(wx, wy), (wx + 10, wy), (wx + 10, wy + 14), (wx, wy + 14)], (70, 64, 50))
        x += w + r.uniform(0, 20)


def zemin(tv, y, renk=(14, 15, 28)):
    tv.cokgen([(-3 * W, y), (4 * W, y), (4 * W, y + 3 * H), (-3 * W, y + 3 * H)], renk)
    tv.cizgi((-3 * W, y), (4 * W, y), (60, 60, 86), 2)


def agac(tv, kok, boy, buyu, tohum=0, yaprak=1.0, dokul=0.0, kar=0.0, t=0.0, renk=KREM):
    """Özyinelemeli çizgi ağaç. buyu 0-1."""
    r = np.random.default_rng(tohum)
    uclar = []

    def dal(p, aci, uz, d, b):
        if d > 6 or b <= 0:
            uclar.append(p); return
        f = min(1, b * 7 - d)
        if f <= 0:
            return
        q = (p[0] + math.sin(aci) * uz * f, p[1] - math.cos(aci) * uz * f)
        tv.cizgi(p, q, renk, max(1.5, 9 - d * 1.4))
        if f < 1:
            return
        for s in (-1, 1):
            dal(q, aci + s * r.uniform(0.25, 0.6), uz * r.uniform(0.62, 0.78), d + 1, b)
        if d == 6:
            uclar.append(q)

    dal(kok, 0, boy * 0.32, 0, buyu)
    rr = np.random.default_rng(tohum + 99)
    for i, u in enumerate(uclar):
        if rr.random() > yaprak:
            continue
        dus = max(0.0, dokul * 1.6 - rr.random() * 0.6)
        y = u[1] + dus * (kok[1] - u[1] + 10)
        x = u[0] + math.sin(dus * 9 + i) * 30 * min(1, dus)
        if y < kok[1] + 5:
            c = renk_kar((120, 160, 110), (220, 140, 70), min(1, dokul * 1.4))
            tv.daire((x, y), 7, c, dolu=True)
        if kar > 0 and rr.random() < kar:
            tv.daire((u[0], u[1] - 4), 5, (230, 236, 246), dolu=True)
    return uclar


def kokler(tv, kok, buyu, yon=1, tohum=5, renk=(200, 170, 120), parla=0.0, hedef=None):
    r = np.random.default_rng(tohum)

    def k(p, aci, uz, d):
        f = min(1, buyu * 6 - d)
        if f <= 0 or d > 5:
            return
        q = (p[0] + math.sin(aci) * uz * f, p[1] + math.cos(aci) * uz * f)
        tv.cizgi(p, q, renk, max(1.5, 6 - d))
        if parla:
            tv.isik(q, 14, renk, parla * 0.4)
        if f < 1:
            return
        for s in (-1, 1):
            k(q, aci + s * r.uniform(0.3, 0.7) + (0.25 * yon if hedef else 0), uz * r.uniform(0.7, 0.85), d + 1)

    k(kok, 0, 120, 0)
