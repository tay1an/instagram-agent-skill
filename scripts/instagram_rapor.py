#!/usr/bin/env python3
"""Son gönderilerin istatistiklerini çekip haftalık rapor yazar.

GitHub Actions tarafından haftada bir çalıştırılır. Son gönderilerin temel
sayılarını (beğeni, yorum) ve izin varsa istatistiklerini (izlenme, erişim,
kaydetme, paylaşma, takip, reel izlenme süresi) çeker; /ig-audit'in
istediği oranları hesaplar ve .claude/instagram/rapor/ altına yazar.

İstatistikler için tokenda instagram_business_manage_insights izni olmalı.
İzin yoksa rapor yalnızca beğeni ve yorumlarla yazılır ve bunu belirtir.

Ortam değişkenleri: IG_ACCESS_TOKEN, isteğe bağlı RAPOR_GONDERI (varsayılan 30).
"""

import json
import os
import statistics
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from instagram_yayinla import ApiHatasi, istek  # noqa: E402

KLASOR = ".claude/instagram/rapor"
ADET = int(os.environ.get("RAPOR_GONDERI", "30"))

# Metrikler gönderi türüne göre değişiyor; desteklenmeyen biri tüm isteği
# düşürdüğü için önce toplu, olmazsa tek tek istenir.
METRIKLER = {
    "REELS": ["views", "reach", "likes", "comments", "saved", "shares", "total_interactions",
              "ig_reels_avg_watch_time"],
    "FEED": ["views", "reach", "likes", "comments", "saved", "shares", "total_interactions",
             "follows", "profile_visits"],
    "STORY": ["views", "reach", "replies", "shares", "navigation"],
}


def istatistik(medya_id, tur, token):
    metrikler = METRIKLER.get(tur, METRIKLER["FEED"])
    try:
        cevap = istek("GET", f"{medya_id}/insights", {"metric": ",".join(metrikler)}, token)
        return {m["name"]: deger(m) for m in cevap.get("data", [])}, None
    except ApiHatasi as toplu_hata:
        sonuc, hata = {}, str(toplu_hata)
        for m in metrikler:
            try:
                cevap = istek("GET", f"{medya_id}/insights", {"metric": m}, token)
                for x in cevap.get("data", []):
                    sonuc[x["name"]] = deger(x)
                hata = None
            except ApiHatasi:
                pass
        return sonuc, (hata if not sonuc else None)


def deger(m):
    v = m.get("values") or [{}]
    d = v[0].get("value")
    if d is None:
        d = (m.get("total_value") or {}).get("value")
    return d


def oran(pay, payda):
    return round(pay / payda, 4) if pay is not None and payda else None


def main():
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token:
        print("IG_ACCESS_TOKEN tanımlı değil.")
        return 1
    ben = istek("GET", "me", {"fields": "user_id,username,followers_count,media_count"}, token)
    kullanici = ben.get("user_id") or ben["id"]
    medya = istek("GET", f"{kullanici}/media", {
        "fields": "id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count",
        "limit": ADET,
    }, token).get("data", [])

    satirlar, izin_hatasi = [], None
    for m in medya:
        tur = m.get("media_product_type") or "FEED"
        ist, hata = istatistik(m["id"], tur, token)
        if hata and not izin_hatasi:
            izin_hatasi = hata
        izlenme = ist.get("views")
        erisim = ist.get("reach")
        satirlar.append({
            "tarih": m["timestamp"][:10],
            "tur": "reel" if tur == "REELS" else ("carousel" if m.get("media_type") == "CAROUSEL_ALBUM" else "gönderi"),
            "aciklama": " ".join((m.get("caption") or "").split())[:70],
            "link": m.get("permalink"),
            "begeni": m.get("like_count"),
            "yorum": m.get("comments_count"),
            "izlenme": izlenme,
            "erisim": erisim,
            "kaydetme": ist.get("saved"),
            "paylasma": ist.get("shares"),
            "takip": ist.get("follows"),
            "ort_izlenme_sn": round(ist["ig_reels_avg_watch_time"] / 1000, 1) if ist.get("ig_reels_avg_watch_time") else None,
            "paylasma_orani": oran(ist.get("shares"), erisim),
            "kaydetme_orani": oran(ist.get("saved"), erisim),
            "takip_orani": oran(ist.get("follows"), erisim),
        })

    olcut = "izlenme" if any(s["izlenme"] for s in satirlar) else "begeni"
    degerler = [s[olcut] for s in satirlar if s[olcut] is not None]
    medyan = statistics.median(degerler) if degerler else None
    for s in satirlar:
        s["kat"] = round(s[olcut] / medyan, 1) if medyan and s[olcut] is not None else None

    bugun = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(KLASOR, exist_ok=True)
    veri = {"tarih": bugun, "hesap": ben.get("username"), "takipci": ben.get("followers_count"),
            "olcut": olcut, "medyan": medyan, "izin_hatasi": izin_hatasi, "gonderiler": satirlar}
    with open(f"{KLASOR}/{bugun}.json", "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    def h(v):
        return "-" if v is None else str(v)

    md = [f"# Instagram raporu, {bugun}", "",
          f"@{ben.get('username')} · {ben.get('followers_count')} takipçi · son {len(satirlar)} gönderi · "
          f"ölçüt: {olcut}, medyan {medyan}", ""]
    if izin_hatasi:
        md += ["**İstatistik izni yok:** yalnızca beğeni ve yorumlar var. "
               "Meta'da instagram_business_manage_insights iznini ekleyip anahtarı yenileyin.", "",
               f"Hata: `{izin_hatasi}`", ""]
    md += ["| tarih | tür | kat | izlenme | erişim | beğeni | yorum | kaydetme | paylaşma | takip | ort. izlenme | açıklama |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in sorted(satirlar, key=lambda s: s["kat"] or 0, reverse=True):
        md.append(f"| {s['tarih']} | {s['tur']} | {h(s['kat'])}x | {h(s['izlenme'])} | {h(s['erisim'])} | "
                  f"{h(s['begeni'])} | {h(s['yorum'])} | {h(s['kaydetme'])} | {h(s['paylasma'])} | "
                  f"{h(s['takip'])} | {h(s['ort_izlenme_sn'])} sn | [{s['aciklama'][:40]}]({s['link']}) |")
    with open(f"{KLASOR}/{bugun}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[:6]))
    print(f"{len(satirlar)} gönderi yazıldı.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ApiHatasi as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)
