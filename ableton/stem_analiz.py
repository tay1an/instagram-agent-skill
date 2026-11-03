"""Suno stem'lerini analiz edip Ableton'da sifirdan kurulacak plani cikarir.

ableton-mcp-extended Ableton'u yonetir ama ses dinleyemez. Bu script o boslugu doldurur:
stem'lerden tempo, ton, bolumler, akor yuruyusu, bas/vokal melodisi ve davul paternini
cikarir; notalari MCP'nin `add_notes_to_clip` formatinda (beat cinsinden) yazar.

Kullanim:
    python stem_analiz.py <stem-klasoru> [--cikti analiz.json] [--bpm 120]

Cikti: <klasor>/analiz.json (ajana verilecek tam veri) ve <klasor>/analiz.md (ozet).
Dosya adindan rol tahmini: vocal, bass, drum, kick, snare, hat, perc, guitar, piano,
keys, synth, pad, lead, string, other... Bilinmeyenler akor stem'i sayilir.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import librosa
import numpy as np

SR = 22050
HOP = 512
SES_UZANTI = {".wav", ".mp3", ".flac", ".aif", ".aiff", ".ogg", ".m4a"}
NOTA = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Krumhansl-Kessler ton profilleri
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

ROLLER = [
    ("vokal", ("vocal", "vox", "voice", "sing", "lead vox", "backing")),
    ("davul", ("drum", "kick", "snare", "hat", "perc", "beat", "cymbal")),
    ("bas", ("bass", "sub", "808")),
    ("melodi", ("lead", "melody", "flute", "sax", "trumpet", "whistle")),
]


def rol_tahmin(ad: str) -> str:
    ad = ad.lower()
    for rol, anahtarlar in ROLLER:
        if any(a in ad for a in anahtarlar):
            return rol
    return "akor"  # guitar, piano, keys, synth, pad, strings, other, instrumental...


def ton_bul(chroma: np.ndarray) -> tuple[str, float]:
    ort = chroma.mean(axis=1)
    en_iyi, skor = "C major", -1.0
    for kok in range(12):
        for profil, tur in ((MAJOR, "major"), (MINOR, "minor")):
            r = float(np.corrcoef(ort, np.roll(profil, kok))[0, 1])
            if r > skor:
                en_iyi, skor = f"{NOTA[kok]} {tur}", r
    return en_iyi, round(skor, 3)


def akor_sablonlari() -> list[tuple[str, np.ndarray, list[int]]]:
    sablon = []
    for kok in range(12):
        for ek, araliklar in (("", (0, 4, 7)), ("m", (0, 3, 7))):
            v = np.zeros(12)
            v[[(kok + a) % 12 for a in araliklar]] = 1
            sablon.append((NOTA[kok] + ek, v / np.linalg.norm(v), [48 + kok + a for a in araliklar]))
    return sablon


class Izgara:
    """Saniye <-> beat donusumu. Suno parcalari sabit tempoludur; ilk vurus beat 0 olur."""

    def __init__(self, bpm: float, ilk_vurus: float):
        self.bpm, self.ilk = bpm, ilk_vurus

    def beat(self, t: float, kuantize: float = 0.25) -> float:
        b = (t - self.ilk) * self.bpm / 60.0
        return round(round(b / kuantize) * kuantize, 4)

    def sn(self, b: float) -> float:
        return self.ilk + b * 60.0 / self.bpm


def yukle(yol: Path) -> np.ndarray:
    y, _ = librosa.load(str(yol), sr=SR, mono=True)
    return y


def monofonik_notalar(y: np.ndarray, iz: Izgara, fmin: str, fmax: str) -> list[dict]:
    f0, voiced, _ = librosa.pyin(y, fmin=librosa.note_to_hz(fmin), fmax=librosa.note_to_hz(fmax),
                                 sr=SR, hop_length=HOP)
    zaman = librosa.times_like(f0, sr=SR, hop_length=HOP)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0][: len(f0)]
    midi = np.where(voiced, np.round(librosa.hz_to_midi(np.nan_to_num(f0, nan=1.0))), -1)
    notalar, i = [], 0
    while i < len(midi):
        if midi[i] < 0:
            i += 1
            continue
        j = i
        while j + 1 < len(midi) and midi[j + 1] == midi[i]:
            j += 1
        bas, son = iz.beat(zaman[i]), iz.beat(zaman[j] + HOP / SR)
        if son - bas >= 0.25 and bas >= 0:
            hiz = int(np.clip(40 + 87 * rms[i:j + 1].max() / (rms.max() + 1e-9), 40, 127))
            notalar.append({"pitch": int(midi[i]), "start_time": bas, "duration": son - bas,
                            "velocity": hiz, "mute": False})
        i = j + 1
    return notalar


def davul_notalari(y: np.ndarray, iz: Izgara) -> list[dict]:
    """Onset'leri spektral merkeze gore kick(36)/snare(38)/hat(42) olarak ayirir."""
    onset = librosa.onset.onset_detect(y=y, sr=SR, hop_length=HOP, units="frames", backtrack=False)
    if len(onset) == 0:
        return []
    merkez = librosa.feature.spectral_centroid(y=y, sr=SR, hop_length=HOP)[0]
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    notalar, gorulen = [], set()
    for f in onset:
        c = merkez[min(f, len(merkez) - 1)]
        pitch = 36 if c < 1500 else (38 if c < 4500 else 42)
        b = iz.beat(librosa.frames_to_time(f, sr=SR, hop_length=HOP))
        if b < 0 or (pitch, b) in gorulen:
            continue
        gorulen.add((pitch, b))
        hiz = int(np.clip(50 + 77 * rms[min(f, len(rms) - 1)] / (rms.max() + 1e-9), 50, 127))
        notalar.append({"pitch": pitch, "start_time": b, "duration": 0.25, "velocity": hiz, "mute": False})
    return notalar


def akorlar(y: np.ndarray, iz: Izgara, toplam_beat: float, beat_per_akor: float = 2.0) -> list[dict]:
    chroma = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP)
    zaman = librosa.times_like(chroma, sr=SR, hop_length=HOP)
    sablon, sonuc, b = akor_sablonlari(), [], 0.0
    while b < toplam_beat:
        m = (zaman >= iz.sn(b)) & (zaman < iz.sn(b + beat_per_akor))
        if m.any():
            v = chroma[:, m].mean(axis=1)
            if v.max() > 0.2:
                v = v / (np.linalg.norm(v) + 1e-9)
                ad, _, perdeler = max(sablon, key=lambda s: float(s[1] @ v))
                if sonuc and sonuc[-1]["ad"] == ad and sonuc[-1]["bitis"] == b:
                    sonuc[-1]["bitis"] = b + beat_per_akor
                else:
                    sonuc.append({"ad": ad, "baslangic": b, "bitis": b + beat_per_akor, "perdeler": perdeler})
        b += beat_per_akor
    return sonuc


def akor_notalari(akor_listesi: list[dict]) -> list[dict]:
    return [{"pitch": p, "start_time": a["baslangic"], "duration": a["bitis"] - a["baslangic"],
             "velocity": 90, "mute": False} for a in akor_listesi for p in a["perdeler"]]


def bolumler(miks: np.ndarray, iz: Izgara, toplam_bar: int) -> list[dict]:
    """Chroma + MFCC benzerligiyle 4 bar katlarinda bolum sinirlari."""
    ozellik = np.vstack([librosa.feature.chroma_cqt(y=miks, sr=SR, hop_length=HOP),
                         librosa.feature.mfcc(y=miks, sr=SR, hop_length=HOP, n_mfcc=13)])
    ozellik = librosa.util.normalize(ozellik, axis=1)
    k = int(np.clip(round(toplam_bar / 8), 2, 12))
    sinir = librosa.segment.agglomerative(ozellik, k)
    sn = librosa.frames_to_time(sinir, sr=SR, hop_length=HOP)
    barlar = sorted({max(0, int(round(iz.beat(t, 1) / 4 / 4)) * 4) for t in sn} | {0})
    barlar = [b for b in barlar if b < toplam_bar] + [toplam_bar]
    return [{"bar_baslangic": a + 1, "bar_bitis": b, "uzunluk_bar": b - a}
            for a, b in zip(barlar, barlar[1:]) if b > a]


def bar_enerjisi(y: np.ndarray, iz: Izgara, toplam_bar: int) -> list[float]:
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    zaman = librosa.times_like(rms, sr=SR, hop_length=HOP)
    tepe, cikti = rms.max() + 1e-9, []
    for bar in range(toplam_bar):
        m = (zaman >= iz.sn(bar * 4)) & (zaman < iz.sn(bar * 4 + 4))
        cikti.append(round(float(rms[m].mean() / tepe), 2) if m.any() else 0.0)
    return cikti


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("klasor", type=Path)
    ap.add_argument("--cikti", type=Path)
    ap.add_argument("--bpm", type=float, help="Suno'dan biliniyorsa tempoyu elle ver")
    a = ap.parse_args()

    dosyalar = sorted(p for p in a.klasor.iterdir() if p.suffix.lower() in SES_UZANTI)
    if not dosyalar:
        sys.exit(f"{a.klasor} icinde ses dosyasi yok")
    print(f"{len(dosyalar)} stem yukleniyor...")
    stemler = {p: yukle(p) for p in dosyalar}
    uzunluk = max(len(y) for y in stemler.values())
    miks = sum(np.pad(y, (0, uzunluk - len(y))) for y in stemler.values())
    roller = {p: rol_tahmin(p.stem) for p in dosyalar}

    ritim = next((y for p, y in stemler.items() if roller[p] == "davul"), miks)
    tempo, vuruslar = librosa.beat.beat_track(y=ritim, sr=SR, hop_length=HOP, units="time")
    bpm = a.bpm or float(np.round(np.atleast_1d(tempo)[0], 1))
    iz = Izgara(bpm, float(vuruslar[0]) if len(vuruslar) else 0.0)
    toplam_beat = iz.beat(uzunluk / SR, 1)
    toplam_bar = int(np.ceil(toplam_beat / 4))

    harmonik = [y for p, y in stemler.items() if roller[p] in ("akor", "bas")] or [miks]
    harm_miks = sum(np.pad(y, (0, uzunluk - len(y))) for y in harmonik)
    ton, ton_guven = ton_bul(librosa.feature.chroma_cqt(y=harm_miks, sr=SR, hop_length=HOP))

    rapor = {
        "bpm": bpm, "ton": ton, "ton_guveni": ton_guven, "olcu": "4/4",
        "ilk_vurus_sn": round(iz.ilk, 3), "sure_sn": round(uzunluk / SR, 2), "toplam_bar": toplam_bar,
        "bolumler": bolumler(miks, iz, toplam_bar),
        "not": "Notalar beat cinsinden, ilk vurus = 0. add_notes_to_clip'e dogrudan verilebilir. "
               "Otomatik transkripsiyon yaklasiktir; ozellikle akorlar ve davul ayrimi kulakla kontrol edilmeli.",
        "stemler": [],
    }
    for p, y in stemler.items():
        rol = roller[p]
        print(f"  {p.name}: {rol}")
        kayit = {"dosya": str(p.resolve()), "rol": rol, "bar_enerjisi": bar_enerjisi(y, iz, toplam_bar)}
        if rol == "davul":
            kayit["notalar"] = davul_notalari(y, iz)
            kayit["midi_harita"] = {"36": "kick", "38": "snare", "42": "hi-hat"}
        elif rol == "bas":
            kayit["notalar"] = monofonik_notalar(y, iz, "E1", "G3")
        elif rol in ("vokal", "melodi"):
            kayit["notalar"] = monofonik_notalar(y, iz, "C3", "C6")
        else:
            kayit["akorlar"] = akorlar(y, iz, toplam_beat)
            kayit["notalar"] = akor_notalari(kayit["akorlar"])
        rapor["stemler"].append(kayit)

    cikti = a.cikti or a.klasor / "analiz.json"
    cikti.write_text(json.dumps(rapor, ensure_ascii=False, indent=1), encoding="utf-8")

    satir = [f"# Stem analizi: {a.klasor.name}", "",
             f"- Tempo: **{bpm} BPM**, ton: **{ton}** (guven {ton_guven}), {toplam_bar} bar", "",
             "## Bolumler", ""]
    satir += [f"- Bar {b['bar_baslangic']}-{b['bar_bitis']} ({b['uzunluk_bar']} bar)" for b in rapor["bolumler"]]
    satir += ["", "## Stemler", ""]
    for s in rapor["stemler"]:
        ek = ""
        if "akorlar" in s:
            ek = " | akorlar: " + " ".join(x["ad"] for x in s["akorlar"][:16])
        satir.append(f"- **{Path(s['dosya']).name}** ({s['rol']}): {len(s['notalar'])} nota{ek}")
    (cikti.with_suffix(".md")).write_text("\n".join(satir) + "\n", encoding="utf-8")
    print(f"\nYazildi: {cikti} ve {cikti.with_suffix('.md')}")
    print(f"Tempo {bpm} BPM, ton {ton}, {toplam_bar} bar, {len(rapor['bolumler'])} bolum")


if __name__ == "__main__":
    main()
