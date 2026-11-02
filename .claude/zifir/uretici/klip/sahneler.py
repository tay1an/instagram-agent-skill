"""Uzak klibinin hikâyesi, saniye saniye. kare(t) -> RGB görüntü (1920x1080)."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from motor import (W, H, KREM, KIRMIZI, SICAK, AY, Tuval, gok, lerp, ease, bol, renk_kar, poz, poz_kar, yuru, adam,
                   kalp, lamba, balonlar, yildizlar, sehir, zemin, agac, kokler)

GY = 860             # sokak zemini
LX = 1150            # lamba
GOK1 = gok()
GOK_SAFAK = gok((20, 24, 60), (210, 120, 90))
OTUR = poz(lth=88, lsh=88, rth=84, rsh=80, lua=20, lfa=-20, rua=14, rfa=-10)
DIZ = poz(lth=80, lsh=150, rth=-10, rsh=0, egim=25, lua=40, lfa=-10, rua=55, rfa=-20)


def yaz_sprite(s, boy, yol="/usr/share/fonts/opentype/inter/Inter-Medium.otf", iz=6):
    f = ImageFont.truetype(yol, boy)
    x0, y0, x1, y1 = f.getbbox(s)
    w = int(f.getlength(s) + iz * (len(s) - 1)) + 10
    im = Image.new("L", (w, y1 - y0 + 10), 0)
    d = ImageDraw.Draw(im)
    x = 5
    for ch in s:
        d.text((x, 5 - y0), ch, font=f, fill=255); x += f.getlength(ch) + iz
    return np.asarray(im, np.float32) / 255


BASLIK = yaz_sprite("ZİFİR  —  UZAK", 64)


def kalp_parca(i):
    r = np.random.default_rng(40 + i)
    return r.uniform(-1, 1), r.uniform(0.6, 1.4), r.uniform(0, 6.28)


# ======================= A: SOKAK (0 - 39) =======================
def sokak(t):
    cy = lerp(-120, 540, ease(bol(t, 0, 4.5)))
    cx, z = 960, 1.0
    if 9.2 <= t < 24.6:
        f = ease(bol(t, 9.2, 10.5)) * (1 - ease(bol(t, 23.5, 24.6)))
        cx, cy, z = lerp(960, 1140, f), lerp(cy, 640, f), lerp(1, 1.3, f)
    renk_t = bol(t, 28.2, 32.1)
    zem = GOK1
    tv = Tuval(zem, cx, cy, z)
    if 28.2 <= t < 33:  # 'başka renk': gökyüzü renk değiştirir
        h = (t - 28.2) / 3.9
        tint = np.array([math.sin(h * 6.28) * 30 + 30, math.sin(h * 6.28 + 2) * 30 + 20, math.sin(h * 6.28 + 4) * 30 + 30], np.float32)
        tv.img = np.clip(tv.img.astype(np.float32) + tint * (1 - ease(bol(t, 32.0, 33))) * min(1, (t - 28.2) * 2), 0, 255).astype(np.uint8)
    yildizlar(tv, t)
    sehir(tv, GY - 10)
    zemin(tv, GY)
    yan = 0.0 if t < 2.5 else (1.0 if t > 3.6 else (1.0 if math.sin(t * 40) > 0.2 else 0.15))
    if 24.6 <= t < 33:
        yan *= 1 + 1.2 * ease(bol(t, 24.6, 25.5))
    kol = lamba(tv, LX, GY, yan, t)
    balonlar(tv, (kol[0] - 10, kol[1] - 6), t)

    # --- karakterler ---
    ax, kx = 1010, 1270
    ap, kp = poz(), poz()
    ayon, kyon = 1, -1
    if t < 9.2:
        a_f = bol(t, 4.5, 9.0); k_f = bol(t, 5.0, 9.0)
        ax = lerp(300, 1010, a_f); kx = lerp(1900, 1270, k_f)
        ap = yuru(t * 7) if 4.5 < t < 9.0 else poz()
        kp = yuru(t * 7 + 1) if 5.0 < t < 9.0 else poz()
        if t < 4.5:
            ax = -200
        if t < 5.0:
            kx = 2200
    sac = t * 5
    gk = None  # kalp konumu
    catlak = 0.0
    if 9.2 <= t < 20.3:
        # kalbi göğsünden çıkarıp verir
        e1 = ease(bol(t, 9.4, 10.4))
        ap = poz_kar(poz(), poz(rua=-60, rfa=-60, lua=10), e1)
        if t >= 10.4:
            e2 = ease(bol(t, 10.4, 11.6))
            ap = poz_kar(poz(rua=-60, rfa=-60), poz(rua=-82, rfa=-8, egim=6), e2)
            kp = poz_kar(poz(), poz(rua=-75, rfa=-20, lua=-70, lfa=-25), ease(bol(t, 10.8, 11.8)))
    if 12.9 <= t < 16.8:
        ap = poz_kar(poz(rua=-82, rfa=-8, egim=6), poz(egim=18, rua=-40, rfa=-95, bas=15), ease(bol(t, 14.6, 15.4)))
        kp = poz(rua=-70 + 40 * math.sin((t - 12.9) * 4), rfa=-30, lua=-40)
    if 16.8 <= t < 20.3:
        ap = poz(egim=18, rua=-40, rfa=-95, bas=15)
        kp = poz(rua=-60, rfa=-30, lua=20, bas=-10)
    if 20.3 <= t < 24.6:
        kp = poz(rua=-20, rfa=-10, bas=10)
        ap = poz_kar(poz(egim=18, rua=-40, rfa=-95, bas=15), DIZ, ease(bol(t, 20.6, 21.4)))
    if 24.6 <= t < 32.1:  # alevde dans: el ele dönerler
        ap = poz_kar(DIZ, poz(rua=-70, rfa=-10), ease(bol(t, 24.6, 25.3)))
        kp = poz(rua=-70, rfa=-10)
        don = ease(bol(t, 25.3, 32.0)) * 4 * math.pi
        mx, r = 1140, 130
        ax, kx = mx - r * math.cos(don), mx + r * math.cos(don)
        ayon = 1 if math.sin(don) >= 0 else -1
        kyon = -ayon
        if math.cos(don) < 0:
            ayon, kyon = kyon, ayon
        ap = poz_kar(ap, yuru(t * 9), 0.4); kp = poz_kar(kp, yuru(t * 9 + 1), 0.4)
    if 32.1 <= t < 35.6:  # çerçeve çizer
        ax, kx, ayon, kyon = 1010, 1270, 1, -1
        ap = poz(rua=-100 + 30 * math.sin((t - 32.1) * 3), rfa=-10)
        kp = poz(bas=-5)
    if t >= 35.6:  # el ele sağa yürürler
        f = bol(t, 35.6, 39)
        ax, kx = lerp(1010, 1700, f), lerp(1130, 1820, f)
        ayon = kyon = 1
        ap, kp = yuru(t * 7), yuru(t * 7 + 0.5)
        tv.cx = lerp(960, 1300, ease(f))
    A = adam(tv, ax, GY, ap, ayon)
    Kz = adam(tv, kx, GY, kp, kyon, kiz=True, sac_faz=sac)

    # --- kalp ---
    if 9.4 <= t < 20.7:
        if t < 10.4:
            gk, rr = A["gogus"], lerp(4, 22, ease(bol(t, 9.4, 10.4)))
        elif t < 11.8:
            gk, rr = (lerp(A["gogus"][0], (A["el_r"][0] + Kz["el_r"][0]) / 2, ease(bol(t, 10.4, 11.8))), lerp(A["gogus"][1], 700, ease(bol(t, 10.4, 11.8)))), 24
        elif t < 12.9:
            gk, rr = (Kz["el_r"][0] - 10, Kz["el_r"][1] - 20), 24
        elif t < 16.8:
            u = (t - 12.9) % 1.3 / 1.3
            gk, rr = (Kz["el_r"][0] - 10, Kz["el_r"][1] - 20 - 260 * 4 * u * (1 - u)), 24
            catlak = ease(bol(t, 14.6, 15.0))
        else:
            gk, rr = (Kz["el_r"][0] - 10, Kz["el_r"][1] - 20), 24
            catlak = 1.0
            if t >= 20.3:
                gk = (gk[0], lerp(gk[1], GY - 20, ease(bol(t, 20.3, 20.7)) ** 2))
        kalp(tv, gk, rr, catlak=catlak, aci=math.sin(t * 3) * 0.2)
    if 20.7 <= t < 26:  # kırılır, parçalar göğe süzülür
        for i in range(6):
            dx, hz, f = kalp_parca(i)
            u = t - 20.7
            px = 1200 + dx * 120 * min(1, u * 3) + math.sin(u * 2 + f) * 20
            py = GY - 20 - 80 * min(1, u * 3) - max(0, u - 0.6) * 160 * hz
            kalp(tv, (px, py), 9, isik=0.5, aci=f + u)
    # --- oklar ve taşlar ---
    if 16.8 <= t < 20.5:
        for j, ts in enumerate((17.1, 18.1, 19.1)):
            tasx = 1560 + j * 120
            u = bol(t, ts, ts + 0.35)
            if 0 < u < 1:
                p = (lerp(Kz["goz"][0], tasx, u), lerp(Kz["goz"][1], GY - 18, u))
                tv.cizgi((p[0] - 40, p[1] - 6 * (1 - u)), p, KREM, 3)
                tv.isik(p, 12, KREM, 0.5)
            if t < ts + 0.35:
                tv.daire((tasx, GY - 18), 18, (110, 108, 120), dolu=True)
            else:
                v = t - ts - 0.35
                for q in range(5):
                    a = q * 1.25 + j
                    tv.daire((tasx + math.cos(a) * 140 * v, GY - 18 - math.sin(a) * 200 * v + 400 * v * v), 6, (110, 108, 120), dolu=True)
    # --- alev ---
    if 24.6 <= t < 32.6:
        g = ease(bol(t, 24.6, 25.6)) * (1 - ease(bol(t, 31.8, 32.6)))
        for i in range(3):
            fx = 1140 + math.sin(t * 9 + i) * 8
            h = (150 + 30 * math.sin(t * 11 + i * 2)) * g * (1 - i * 0.25)
            tv.cokgen([(fx - 40 * g, GY), (fx, GY - h), (fx + 40 * g, GY)], renk_kar(SICAK, (255, 90, 50), i * 0.4))
        tv.isik((1140, GY - 80), 260 * g, SICAK, 0.9 * g)
    # --- çiçekler ---
    if 28.2 <= t < 37:
        for i in range(14):
            x = 760 + i * 60 + (i % 3) * 13
            b = ease(bol(t, 28.4 + i * 0.22, 28.9 + i * 0.22))
            if b <= 0:
                continue
            h = 50 + (i * 37 % 40)
            tv.cizgi((x, GY), (x, GY - h * b), (110, 170, 110), 3)
            c = [(240, 120, 150), (250, 200, 90), (150, 140, 240), (240, 160, 90)][i % 4]
            tv.daire((x, GY - h * b), 11 * b, c, dolu=True)
    # --- çerçeve ---
    if 32.1 <= t < 37:
        x0, y0, x1, y1 = 1190, 600, 1350, 790
        cerceve(tv, x0, y0, x1, y1, ease(bol(t, 32.3, 33.6)), parla=ease(bol(t, 33.6, 34.4)) * (1 - ease(bol(t, 35.6, 36.4))))
    return tv


def cerceve(tv, x0, y0, x1, y1, ciz, parla=0.0, ici=True):
    kenar = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    top = 4 * ((x1 - x0) + (y1 - y0)) / 2
    pts, kalan = [kenar[0]], ciz * top
    for a, b in zip(kenar, kenar[1:]):
        d = math.dist(a, b)
        if kalan <= 0:
            break
        f = min(1, kalan / d)
        pts.append((lerp(a[0], b[0], f), lerp(a[1], b[1], f)))
        kalan -= d
    tv.yol(pts, (240, 210, 140), 4)
    if parla > 0 and ici:
        tv.isik(((x0 + x1) / 2, (y0 + y1) / 2), 90, (255, 210, 120), parla)
        mx = (x0 + x1) / 2
        o = (y1 - y0) / 260
        adam(tv, mx, y1 - 10, poz(), -1, o=o, renk=renk_kar(KREM, (255, 215, 120), parla), kiz=True)


# ======================= B: İSKELE (38 - 66.6) =======================
SU = 720
GV = 700  # iskele güvertesi


def iskele(t):
    cx, cy, z = 960, 540, 1.0
    if 43.8 <= t < 47.6:
        f = ease(bol(t, 43.8, 47.6)); z = lerp(1, 1.15, f); cy = lerp(540, 500, f)
    if t >= 47.6:
        z, cy = 1.15, 500
    if t >= 51.4:
        f = ease(bol(t, 51.4, 54.5)); cx = lerp(960, 700, f); z = lerp(1.15, 1.0, f); cy = lerp(500, 540, f)
    tv = Tuval(GOK1, cx, cy, z)
    yildizlar(tv, t, tohum=8)
    ay_y = lerp(780, 380, ease(bol(t, 38, 47)))
    tv.daire((1500, ay_y), 70, AY, dolu=True)
    tv.isik((1500, ay_y), 180, AY, 0.5)
    tv.cokgen([(-2 * W, SU), (3 * W, SU), (3 * W, 3 * H), (-2 * W, 3 * H)], (12, 16, 34))
    for i in range(30):  # su ışıltısı
        y = SU + 12 + i * 12
        w = 30 + 120 * (1 - i / 30)
        x = 1500 + math.sin(t * 2 + i) * 20
        tv.cizgi((x - w / 2, y), (x + w / 2, y), renk_kar((12, 16, 34), AY, 0.5 * (1 - i / 30)), 2)
    tv.cokgen([(-W, GV), (1320, GV), (1320, GV + 14), (-W, GV + 14)], (70, 62, 66))
    for px in range(-800, 1320, 160):
        tv.cizgi((px, GV + 14), (px, SU + 60), (60, 54, 58), 8)

    sac = t * 5
    adam_cozul = 0.0
    if t < 47.6:  # yan yana otururlar
        sal = math.sin(t * 2.2) * 14
        ap = poz_kar(OTUR, poz(), 0); ap = dict(OTUR); ap["lsh"] += sal; ap["rsh"] -= sal
        kp = dict(OTUR); kp["lsh"] -= sal; kp["rsh"] += sal; kp["lua"] = -30
        if t < 39.5:  # iskeleye gelip otururlar
            f = ease(bol(t, 38, 39.5))
            A = adam(tv, 1150, GV + 56 * f + 0, poz_kar(poz(), OTUR, f), 1)
            Kz = adam(tv, 1235, GV + 56 * f, poz_kar(poz(), OTUR, f), 1, kiz=True, sac_faz=sac)
        else:
            A = adam(tv, 1150, GV + 56, ap, 1)
            Kz = adam(tv, 1235, GV + 56, kp, 1, kiz=True, sac_faz=sac)
        if t >= 43.8:  # hayal balonu: ufukta bir ev
            f = ease(bol(t, 43.8, 45.0))
            b = A["bas"]
            for i, (dx, dy, r) in enumerate(((30, -40, 8), (60, -80, 12))):
                if f > i * 0.3:
                    tv.daire((b[0] + dx, b[1] + dy), r, KREM, 3)
            if f > 0.6:
                c = (b[0] + 150, b[1] - 170)
                tv.daire(c, 95 * ease((f - 0.6) / 0.4), KREM, 3)
                o = ease((f - 0.6) / 0.4)
                tv.yol([(c[0] - 40 * o, c[1] + 30 * o), (c[0] - 40 * o, c[1] - 10 * o), (c[0], c[1] - 45 * o), (c[0] + 40 * o, c[1] - 10 * o), (c[0] + 40 * o, c[1] + 30 * o), (c[0] - 40 * o, c[1] + 30 * o)], SICAK, 3)
                tv.isik(c, 60 * o, SICAK, 0.5)
                adam(tv, c[0] - 60 * o, c[1] + 30 * o, poz(), 1, o=0.25 * o)
                adam(tv, c[0] + 60 * o, c[1] + 30 * o, poz(), -1, o=0.25 * o, kiz=True)
    else:
        f = ease(bol(t, 47.6, 49))
        ap = poz_kar(OTUR, poz(), ease(bol(t, 50.5, 51.6)))
        kp = poz_kar(OTUR, poz(rua=5), f)
        kx = 1235
        kyon = 1
        if t >= 51.4:
            kyon = -1
            kx = lerp(1235, -300, ease(bol(t, 51.4, 58)))
            kp = yuru(t * 6)
        ayon = 1 if t < 51.4 else -1
        if t >= 51.6:
            ap = poz(rua=-85, rfa=-5, egim=10)
        adam_cozul = bol(t, 54.5, 58.5)
        A = adam(tv, 1150, lerp(GV + 56, GV, ease(bol(t, 50.5, 51.6))), ap, ayon,
                 renk=renk_kar(KREM, (60, 60, 86), adam_cozul * 0.7))
        Kz = adam(tv, kx, lerp(GV + 56, GV, f), kp, kyon, kiz=True, sac_faz=sac)
        el = Kz["el_l"] if kyon == 1 else Kz["el_r"]
        tv.cokgen([(el[0] - 22, el[1]), (el[0] + 22, el[1]), (el[0] + 22, el[1] + 36), (el[0] - 22, el[1] + 36)], (150, 90, 70))
        if t >= 47.6:  # uzayan gölge
            tv.cizgi((kx, GV - 2), (kx + 260 * f, GV - 2), (24, 24, 40), 10)
        if adam_cozul > 0:  # adamın bedeni toz olup kıza doğru savrulur
            rr = np.random.default_rng(7)
            for i in range(90):
                bas_t = rr.uniform(0, 1)
                u = (adam_cozul - bas_t * 0.6)
                if u <= 0:
                    continue
                ox, oy = 1150 + rr.uniform(-25, 25), GV - rr.uniform(0, 210)
                tv.daire((ox - u * rr.uniform(300, 900), oy - math.sin(u * 3 + i) * 40), 2.5, KREM, dolu=True)
    if 59.0 <= t < 63:  # boş çerçeve suya düşer
        f = bol(t, 59.0, 61.0)
        y = lerp(420, SU + 10, f ** 2)
        if t < 61.2:
            cerceve(tv, 880, y - 90, 980, y + 30, 1.0, ici=False)
        else:
            for k in range(3):
                r = (t - 61.2) * 160 + k * 40
                tv.yol([(930 + math.cos(a) * r, SU + 14 + math.sin(a) * r * 0.18) for a in np.linspace(0, 6.3, 50)], renk_kar((12, 16, 34), KREM, max(0, 1 - (t - 61.2) / 1.8)), 2)
    return tv


def yalniz_kiz(t):
    """62.9-66.6: kız uzakta tek başına, döner; adam olmadan silikleşir."""
    tv = Tuval(GOK1, 960, 540, 1.0)
    yildizlar(tv, t, tohum=11, yogun=0.6)
    zemin(tv, 760)
    f = bol(t, 62.9, 66.6)
    titre = 0.5 + 0.5 * math.sin(t * 23) * math.sin(t * 7)
    renk = renk_kar(KREM, (40, 40, 60), 0.3 + 0.5 * f * titre)
    yon = -1 if t < 64.2 else 1
    p = yuru(t * 5) if t < 64.0 else poz(bas=-12)
    adam(tv, lerp(1100, 1000, ease(bol(t, 62.9, 64))), 760, p, yon, renk=renk, kiz=True, sac_faz=t * 5)
    return tv


# ======================= C: AĞAÇLAR VE KÖKLER (66.6 - 86) =======================
YZ = 560


def agaclar(t):
    cy = 540
    cy = lerp(540, 820, ease(bol(t, 69.7, 72))) if t < 79.7 else lerp(820, 540, ease(bol(t, 79.7, 81.5)))
    tv = Tuval(GOK1, 960, cy, 1.0)
    yildizlar(tv, t, tohum=4)
    tv.cokgen([(-W, YZ), (3 * W, YZ), (3 * W, 3 * H), (-W, 3 * H)], (26, 20, 22))
    tv.cizgi((-W, YZ), (3 * W, YZ), (90, 80, 70), 3)
    g = ease(bol(t, 66.8, 69.5))
    dokul = bol(t, 80.5, 84)
    kar = bol(t, 83.5, 86)
    for x, kiz, tohum in ((480, False, 2), (1440, True, 6)):
        if g < 1:
            adam(tv, x, YZ, poz(lua=-20 - 140 * g, rua=-20 - 140 * g, lfa=-10, rfa=-10), 1 if not kiz else -1,
                 renk=renk_kar(KREM, (60, 60, 86), g), kiz=kiz)
        agac(tv, (x, YZ), 420, g, tohum=tohum, yaprak=1.0, dokul=dokul if not kiz else 0.0, kar=kar)
        kokler(tv, (x, YZ), ease(bol(t, 69.9, 78)), yon=1 if not kiz else -1, tohum=tohum + 1,
               parla=0.6 * bol(t, 74, 78), hedef=True)
    if kar > 0:
        rr = np.random.default_rng(3)
        for i in range(120):
            x = rr.uniform(0, W); sp = rr.uniform(40, 90)
            y = (rr.uniform(0, H) + (t - 83.5) * sp) % H - 100
            tv.daire((x + math.sin(t + i) * 10, y), 3, (230, 236, 246), dolu=True)
    return tv


# ======================= D: YALNIZ LAMBA, GÖZYAŞI, KANATLAR (86 - 103.3) =======================
def kanat_sahne(t):
    cx, cy, z = 1080, 600, 1.0
    if t < 93.5:
        f = ease(bol(t, 86, 92)); cx, cy, z = lerp(1080, 1090, f), lerp(600, 640, f), lerp(1.0, 2.2, f)
    else:
        f = ease(bol(t, 93.5, 97)); cx, cy, z = lerp(1090, 1080, f), lerp(640, 600, f), lerp(2.2, 1.0, f)
    tv = Tuval(GOK1, cx, cy, z)
    yildizlar(tv, t)
    sehir(tv, GY - 10)
    zemin(tv, GY)
    kol = lamba(tv, LX, GY, 1.0, t)
    balonlar(tv, (kol[0] - 10, kol[1] - 6), t)
    if t < 98:  # kar yağmaya devam
        rr = np.random.default_rng(9)
        for i in range(70):
            x = rr.uniform(400, 1800); sp = rr.uniform(30, 60)
            y = (rr.uniform(0, H) + t * sp) % 900 + 100
            tv.daire((x, y), 2.5, renk_kar((60, 60, 80), (230, 236, 246), 1 - bol(t, 96, 98)), dolu=True)
    tv.cokgen([(980, GY - 50), (1210, GY - 50), (1210, GY - 40), (980, GY - 40)], (80, 70, 60))  # bank
    tv.cizgi((1000, GY - 40), (1000, GY), (80, 70, 60), 6); tv.cizgi((1190, GY - 40), (1190, GY), (80, 70, 60), 6)
    kanat = ease(bol(t, 96.5, 100))
    cirp = math.sin((t - 100) * 9) if t > 100 else 0
    if t < 94.5:
        p = dict(OTUR); p["egim"] = 22; p["bas"] = 25; p["lua"] = 35; p["rua"] = 30
        A = adam(tv, 1095, GY - 50 + 56, p, 1)
    else:
        f = ease(bol(t, 94.5, 96))
        p = poz_kar(OTUR, poz(bas=-25, lua=20, rua=-20), f)
        yuk = max(0, t - 101.5) * 60
        A = adam(tv, 1095, lerp(GY - 50 + 56, GY, f) - yuk, p, 1, kanat=kanat, kanat_cirp=cirp)
    # gözyaşı
    if 90.5 <= t < 93.6:
        g = A["goz"] if t < 94.5 else (1105, 0)
        u = bol(t, 91.3, 93.5)
        y = lerp(g[1] + 4, GY, u ** 2)
        r = lerp(2.5, 4.5, ease(bol(t, 90.5, 91.3)))
        tv.cokgen([(g[0] + 6, y - r * 2.2), (g[0] + 6 + r, y), (g[0] + 6, y + r), (g[0] + 6 - r, y)], (190, 220, 255))
        tv.isik((g[0] + 6, y), 10, (190, 220, 255), 0.7)
    if t >= 93.5:  # damla yere değer, halka halka ışık yayılır
        for k in range(4):
            r = (t - 93.5 - k * 0.45) * 380
            if r <= 0:
                continue
            a = max(0, 1 - r / 1400)
            tv.yol([(1101 + math.cos(q) * r, GY + math.sin(q) * r * 0.16) for q in np.linspace(0, 6.3, 80)], renk_kar((14, 15, 28), (190, 220, 255), a), 3)
            tv.isik((1101, GY), 40 + r * 0.1, (150, 190, 255), a * 0.3)
    return tv


# ======================= E: UÇUŞ (101.5 - 123.6) =======================
def ucus(t):
    safak = ease(bol(t, 111.5, 118))
    zem = (GOK1.astype(np.float32) * (1 - safak) + GOK_SAFAK.astype(np.float32) * safak).astype(np.uint8)
    yuk = ease(bol(t, 103.3, 108))
    tv = Tuval(zem, 960, lerp(560, -1400, yuk), 1.0)
    yildizlar(tv, t, n=220, tohum=13, yogun=1 - safak * 0.8)
    if yuk < 0.99:
        sehir(tv, GY - 10); zemin(tv, GY)
        kol = lamba(tv, LX, GY, 1.0, t)
        balonlar(tv, (kol[0] - 10, kol[1] - 6), t)
    # bulutlar
    for i in range(7):
        x = (2400 - (t - 103) * (180 + i * 30) + i * 420) % 2800 - 400
        y = tv.cy - 420 + ((i * 3) % 7) * 125
        a = renk_kar((40, 44, 70), (240, 200, 190), safak * 0.7)
        for k in range(4):
            tv.daire((x + k * 50, y + math.sin(k) * 10), 40 + k * 6, a, dolu=True)
    # adam: önce dikey yükselir, sonra öne eğilip uçar
    ucuyor = ease(bol(t, 107.7, 109))
    x = lerp(1095, 900, ucuyor) + math.sin(t * 1.3) * 30
    y = lerp(GY - 200 - (t - 101.5) * 60, tv.cy + 120, ease(bol(t, 103.3, 107.7))) + math.sin(t * 2) * 12
    p = poz_kar(poz(bas=-25, lua=20, rua=-20), poz(egim=62, bas=-40, lua=-150, lfa=0, rua=-150, rfa=0, lth=-20, rth=-30, lsh=20, rsh=10), ucuyor)
    if t >= 115.4:  # parçaları toplarken kollarını açar
        p = poz_kar(p, poz(egim=20, bas=-10, lua=-80, rua=-80, lfa=-20, rfa=-20), ease(bol(t, 115.4, 116.5)))
    A = adam(tv, x, y, p, 1, kanat=1.0, kanat_cirp=math.sin(t * 9))
    if t >= 115.4:  # kalp parçalarını toplar, kalp birleşir
        hedef = (x + 60, y - 150)
        for i in range(6):
            dx, hz, f = kalp_parca(i)
            ts = 116 + i * 0.8
            u = ease(bol(t, ts, ts + 1.2))
            bas = (x + 600 * dx + 300, y - 400 + 200 * hz)
            px, py = lerp(bas[0], hedef[0], u), lerp(bas[1], hedef[1], u)
            if t < 121.8:
                kalp(tv, (px + math.sin(t * 2 + f) * 10 * (1 - u), py), 9, isik=0.5, aci=f * (1 - u))
        if t >= 121.6:
            g = ease(bol(t, 121.6, 122.6))
            kalp(tv, hedef, lerp(14, 34, g), isik=0.6 + 0.8 * g)
    return tv


# ======================= F: AY (123.6 - 156.3) =======================
def ay_sahne(t):
    """Adam aya uçar, konar; dünyaya bakar."""
    tv = Tuval(GOK1, 960, 540, 1.0)
    yildizlar(tv, t, n=220, tohum=21)
    yak = ease(bol(t, 123.6, 127.3))
    ay_r = lerp(120, 1400, yak)
    ay_c = (lerp(1500, 960, yak), lerp(380, 540 + 1400 + 80, yak))
    tv.daire(ay_c, ay_r, AY, dolu=True)
    tv.isik(ay_c, ay_r * 1.3, AY, 0.35 * (1 - yak))
    for i, (dx, dy, r) in enumerate(((-0.3, -0.2, 0.12), (0.25, 0.1, 0.08), (0.05, 0.35, 0.1))):
        tv.daire((ay_c[0] + dx * ay_r, ay_c[1] + dy * ay_r), r * ay_r, (222, 216, 198), dolu=True)
    yuzey = ay_c[1] - ay_r
    dunya = (380, 230)
    if yak > 0.6:  # gökte dünya
        tv.daire(dunya, 90, (60, 110, 190), dolu=True)
        tv.yol([(dunya[0] - 60, dunya[1] - 20), (dunya[0] - 10, dunya[1] - 40), (dunya[0] + 30, dunya[1] + 10)], (90, 160, 110), 14)
        tv.isik(dunya, 140, (90, 140, 230), 0.4 * ease((yak - 0.6) / 0.4))
    kon = ease(bol(t, 126.8, 127.6))
    x = lerp(300, 1000, ease(bol(t, 123.6, 127)))
    y = lerp(lerp(800, 400, yak), yuzey, kon) if yak < 1 else yuzey
    p = poz_kar(poz(egim=62, bas=-40, lua=-150, lfa=0, rua=-150, rfa=0, lth=-20, rth=-30, lsh=20, rsh=10), poz(lua=-40, lfa=-60, rua=-40, rfa=-60, bas=-20), kon)
    birak = 134.3
    if t >= 131.2:
        p = poz(lua=-40, lfa=-60, rua=-40, rfa=-60, bas=-35)
    if t >= birak:
        p = poz_kar(p, poz(lua=-150, rua=-150, lfa=0, rfa=0, bas=-40), ease(bol(t, birak, birak + 0.8)))
    A = adam(tv, x, y, p, -1, kanat=1.0 - 0.6 * kon, kanat_cirp=math.sin(t * 9) * (1 - kon))
    el = ((A["el_l"][0] + A["el_r"][0]) / 2, min(A["el_l"][1], A["el_r"][1]) - 30)
    if t < birak:
        kalp(tv, el, 34, isik=1.2)
    else:  # kalp dünyaya doğru süzülür
        u = ease(bol(t, birak, 138.8))
        kalp(tv, (lerp(el[0], dunya[0], u), lerp(el[1], dunya[1], u) - math.sin(u * 3.14) * 120), lerp(34, 6, u), isik=1.2)
    return tv


def dunya_sahne(t):
    """Dünyada kız lamba altında, elinde boş çerçeve; kalp gökten iner."""
    tv = Tuval(GOK1, 1150, 600, 1.15)
    yildizlar(tv, t)
    sehir(tv, GY - 10)
    zemin(tv, GY)
    kol = lamba(tv, LX, GY, 1.0, t)
    balonlar(tv, (kol[0] - 10, kol[1] - 6), t)
    tv.daire((1500, 200), 26, AY, dolu=True); tv.isik((1500, 200), 60, AY, 0.4)
    bak = ease(bol(t, 142.6, 143.6))
    p = poz_kar(poz(lua=-60, lfa=-40, rua=-60, rfa=-40, bas=20), poz(lua=-60, lfa=-40, rua=-60, rfa=-40, bas=-40), bak)
    K = adam(tv, 1250, GY, p, -1, kiz=True, sac_faz=t * 4)
    x0, y0 = K["el_l"][0] - 60, K["el_l"][1] - 150
    parla = ease(bol(t, 139.2, 140.5))
    cerceve(tv, x0, y0, x0 + 110, y0 + 140, 1.0, parla=parla)
    if t >= 134.3:  # kalp iner
        u = ease(bol(t, 135.0, 139.0))
        c = (lerp(1500, x0 + 55, u) + math.sin(t * 2) * 20 * (1 - u), lerp(-80, y0 - 30, u))
        if t < 140.2:
            kalp(tv, c, lerp(10, 26, u), isik=1.0)
        else:
            kalp(tv, (x0 + 55, y0 + 70), 22, isik=1.4)
    return tv


def baglanti(t):
    """145.5-176.8: dünya ve ay; ikisinde ağaç büyür, ışıktan kökler gökte birleşir; kapanış."""
    z = lerp(1.0, 0.82, ease(bol(t, 166, 176)))
    tv = Tuval(GOK1, 960, 540, z)
    yildizlar(tv, t, n=240, tohum=31)
    ay_c, dunya_c = (1550, 260), (300, 1500)
    tv.daire(ay_c, 170, AY, dolu=True); tv.isik(ay_c, 260, AY, 0.45)
    tv.daire(dunya_c, 760, (36, 70, 120), dolu=True); tv.isik((560, 820), 300, (90, 140, 230), 0.25)
    ay_kok, dunya_kok = (1490, 96), (560, 754)
    g = ease(bol(t, 145.5, 149.5))
    agac(tv, dunya_kok, 300, g, tohum=6)
    adam(tv, 640, 756, poz(bas=-35, lua=-60, lfa=-40), -1, o=0.7, kiz=True, sac_faz=t * 4)
    kalp(tv, (590, 650), 12, isik=1.0)
    # ay ağacı: aşağı doğru (ayın altında, dünyaya bakan yüzde)
    agac(tv, (1430, 418), 260, g, tohum=9)
    adam(tv, 1500, 425, poz(bas=-30), -1, o=0.6)
    # ışıktan kökler gökte birbirine uzanır
    b = ease(bol(t, 149.5, 155.5))
    for (s, e, tohum) in (((640, 470), (1100, 360), 1), ((1400, 300), (1100, 360), 2)):
        rr = np.random.default_rng(tohum)
        pts = [s]
        for i in range(1, 25):
            f = i / 24
            if f > b:
                break
            pts.append((lerp(s[0], e[0], f) + math.sin(f * 9 + tohum) * 40 * (1 - f), lerp(s[1], e[1], f) - math.sin(f * 3.14) * 120))
        tv.yol(pts, (255, 210, 130), 4)
        for q in pts[::3]:
            tv.isik(q, 16, (255, 200, 120), 0.4 + 0.4 * math.sin(t * 4 + q[0]))
    if b >= 1:
        nab = 0.5 + 0.5 * math.sin((t - 155.5) * 4)
        tv.isik((1100, 360), 60 + 30 * nab, (255, 220, 150), 0.8)
    if t >= 156.3:  # balonlar ışık boyunca yükselir
        u = bol(t, 156.3, 166)
        for i, c in enumerate(((236, 176, 186), (236, 176, 186))):
            f = min(1, max(0, u * 1.2 - i * 0.15))
            px, py = lerp(700, 1100, f) + math.sin(t * 2 + i) * 15, lerp(560, 360, f) - math.sin(f * 3.14) * 120 - i * 40
            tv.cizgi((px, py + 30), (px - 5, py + 110), (150, 140, 150), 2)
            tv.daire((px, py), 22, c, dolu=True)
    return tv


# ======================= ZAMAN ÇİZELGESİ =======================
SAHNELER = [
    (0.0, 38.4, sokak),
    (37.6, 62.9, iskele),
    (62.9, 66.6, yalniz_kiz),
    (66.6, 86.0, agaclar),
    (86.0, 103.6, kanat_sahne),
    (103.3, 123.6, ucus),
    (123.6, 131.2, ay_sahne),
    (131.2, 134.3, dunya_sahne),
    (134.3, 138.8, ay_sahne),
    (138.8, 145.5, dunya_sahne),
    (145.5, 176.8, baglanti),
]
GECIS = 0.5


def kare(t):
    aktif = [s for s in SAHNELER if s[0] <= t < s[1]]
    if not aktif:
        return np.zeros((H, W, 3), np.uint8)
    son = aktif[-1]
    img = son[2](t).bitir()
    if len(aktif) > 1:  # örtüşen sahneler arasında yumuşak geçiş
        w = ease(bol(t, son[0], aktif[-2][1]))
        img = (aktif[-2][2](t).bitir().astype(np.float32) * (1 - w) + img.astype(np.float32) * w).astype(np.uint8)
    elif t - son[0] < GECIS and son[0] > 0:  # kesme yerine kısa karartma
        img = (img.astype(np.float32) * ease((t - son[0]) / GECIS)).astype(np.uint8)
    if t >= 167:  # başlık ve kararma
        a = ease(bol(t, 168, 171)) * (1 - ease(bol(t, 175, 176.8)))
        h, w = BASLIK.shape
        y0, x0 = 900, (W - w) // 2
        bol_ = img[y0:y0 + h, x0:x0 + w].astype(np.float32)
        img[y0:y0 + h, x0:x0 + w] = (bol_ * (1 - BASLIK[..., None] * a) + np.array(KREM, np.float32) * BASLIK[..., None] * a).astype(np.uint8)
        img = (img.astype(np.float32) * (1 - ease(bol(t, 175, 176.8)))).astype(np.uint8)
    return img
