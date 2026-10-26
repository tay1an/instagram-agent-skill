#!/usr/bin/env python3
"""Takvimde zamanı gelen Instagram paylaşımlarını yayınlar.

GitHub Actions tarafından düzenli aralıklarla çalıştırılır. Takvim dosyasındaki
"bekliyor" durumundaki ve zamanı gelmiş her paylaşımı Instagram API (Instagram
Login, graph.instagram.com) üzerinden yayınlar, sonucu takvime geri yazar.

Gereken ortam değişkenleri:
  IG_ACCESS_TOKEN     Instagram uzun ömürlü erişim anahtarı
  GITHUB_REPOSITORY   sahip/depo (Actions otomatik verir)
  GITHUB_SHA          medyanın herkese açık adresi için commit (Actions verir)

İsteğe bağlı:
  IG_API_VERSION      varsayılan v23.0
  TAKVIM              takvim dosyası yolu
  KURU_CALISMA=1      hiçbir şey yayınlamaz, yalnızca ne yapılacağını yazar
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TAKVIM = os.environ.get("TAKVIM", ".claude/instagram/yayin/takvim.json")
API_VERSION = os.environ.get("IG_API_VERSION", "v23.0")
API = f"https://graph.instagram.com/{API_VERSION}"

# Zamanı bundan daha eski kaçırılmış paylaşımlar yayınlanmaz, "atlandi" olur.
# Sabah hikâyesinin akşam çıkması istenmez.
EN_FAZLA_GECIKME = timedelta(hours=3)
EN_FAZLA_DENEME = 3

GORSEL_UZANTILARI = (".jpg", ".jpeg")
VIDEO_UZANTILARI = (".mp4", ".mov")
TURLER = ("gonderi", "hikaye", "reel", "carousel")


class ApiHatasi(Exception):
    pass


def istek(yontem, yol, params, token):
    params = dict(params, access_token=token)
    veri = urllib.parse.urlencode(params).encode()
    url = f"{API}/{yol}"
    if yontem == "GET":
        req = urllib.request.Request(f"{url}?{veri.decode()}")
    else:
        req = urllib.request.Request(url, data=veri, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as yanit:
            return json.load(yanit)
    except urllib.error.HTTPError as e:
        govde = e.read().decode(errors="replace")
        try:
            hata = json.loads(govde)["error"]
            mesaj = hata["message"]
            # Kod ve alt kod, "API access blocked" gibi genel mesajların nedenini ayırt eder.
            ek = ", ".join(f"{k}={hata[k]}" for k in ("code", "error_subcode", "type", "error_user_title", "error_user_msg")
                           if hata.get(k) not in (None, ""))
            if ek:
                mesaj = f"{mesaj} ({ek})"
        except (ValueError, KeyError):
            mesaj = govde[:300]
        raise ApiHatasi(f"{e.code}: {mesaj}") from None


def medya_url(yol):
    depo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    return f"https://raw.githubusercontent.com/{depo}/{sha}/{urllib.parse.quote(yol)}"


def medya_parametresi(yol):
    """Dosya uzantısına göre image_url ya da video_url döndürür."""
    kucuk = yol.lower()
    if kucuk.endswith(GORSEL_UZANTILARI):
        return {"image_url": medya_url(yol)}, False
    if kucuk.endswith(VIDEO_UZANTILARI):
        return {"video_url": medya_url(yol)}, True
    raise ValueError(f"{yol}: görsel .jpg, video .mp4/.mov olmalı (Instagram PNG kabul etmez)")


def hazir_olmasini_bekle(kap_id, token, sure=300):
    bitis = time.monotonic() + sure
    while True:
        durum = istek("GET", kap_id, {"fields": "status_code,status"}, token)
        kod = durum.get("status_code")
        if kod == "FINISHED":
            return
        if kod in ("ERROR", "EXPIRED"):
            raise ApiHatasi(f"medya işlenemedi: {durum.get('status', kod)}")
        if time.monotonic() > bitis:
            raise ApiHatasi("medya 5 dakikada hazır olmadı")
        time.sleep(5)


def kap_olustur(kullanici, params, video, token):
    kap = istek("POST", f"{kullanici}/media", params, token)["id"]
    hazir_olmasini_bekle(kap, token, sure=300 if video else 60)
    return kap


def yayinla(paylasim, kullanici, token):
    tur = paylasim["tur"]
    medya = paylasim["medya"]
    aciklama = paylasim.get("aciklama", "")

    if tur == "carousel":
        if not 2 <= len(medya) <= 10:
            raise ValueError("carousel 2 ile 10 arasında medya ister")
        cocuklar = []
        for yol in medya:
            p, video = medya_parametresi(yol)
            p["is_carousel_item"] = "true"
            if video:
                p["media_type"] = "VIDEO"
            cocuklar.append(kap_olustur(kullanici, p, video, token))
        params = {"media_type": "CAROUSEL", "children": ",".join(cocuklar), "caption": aciklama}
        kap = kap_olustur(kullanici, params, False, token)
    else:
        if len(medya) != 1:
            raise ValueError(f"{tur} tek medya ister")
        params, video = medya_parametresi(medya[0])
        if tur == "hikaye":
            params["media_type"] = "STORIES"
        elif tur == "reel":
            if not video:
                raise ValueError("reel için video gerekir")
            params.update(media_type="REELS", share_to_feed="true", caption=aciklama)
            if paylasim.get("kapak"):
                params["cover_url"] = medya_url(paylasim["kapak"])
        else:
            if video:
                raise ValueError("video gönderiler reel olarak eklenmeli")
            params["caption"] = aciklama
        kap = kap_olustur(kullanici, params, video, token)

    return istek("POST", f"{kullanici}/media_publish", {"creation_id": kap}, token)["id"]


def dogrula(paylasim):
    for alan in ("id", "tur", "zaman", "medya"):
        if alan not in paylasim:
            raise ValueError(f"'{alan}' alanı eksik")
    if paylasim["tur"] not in TURLER:
        raise ValueError(f"tür {TURLER} içinden biri olmalı")
    for yol in paylasim["medya"]:
        if not os.path.isfile(yol):
            raise ValueError(f"{yol} bulunamadı")
        medya_parametresi(yol)


def baglanti_kontrol(token):
    """Deneme modunda hiçbir şey paylaşmadan anahtarı ve izinleri sınar."""
    try:
        ben = istek("GET", "me", {"fields": "user_id,username,account_type"}, token)
        print(f"Bağlantı tamam: @{ben.get('username')} ({ben.get('account_type')})")
        kullanici = ben.get("user_id") or ben["id"]
        limit = istek("GET", f"{kullanici}/content_publishing_limit", {"fields": "quota_usage,config"}, token)
        veri = (limit.get("data") or [{}])[0]
        kota = veri.get("config", {}).get("quota_total")
        print(f"Paylaşım izni tamam: son 24 saatte {veri.get('quota_usage', 0)}/{kota} API paylaşımı")
    except ApiHatasi as e:
        print(f"BAĞLANTI HATASI: {e}", file=sys.stderr)
        # Anahtarın kendisi yazılmaz; yalnızca yanlış metin mi kopyalandı anlaşılsın diye.
        print(f"Anahtar {len(token)} karakter, '{token[:2]}' ile başlıyor"
              f"{', içinde boşluk var' if any(c.isspace() for c in token) else ''}.", file=sys.stderr)
        raise SystemExit(1)


def main():
    kuru = os.environ.get("KURU_CALISMA") == "1"
    # Elle yapıştırılan anahtarlarda baştaki/sondaki boşluk ve satır sonu sık görülür.
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if kuru and token:
        baglanti_kontrol(token)
    with open(TAKVIM, encoding="utf-8") as f:
        takvim = json.load(f)
    dilim = ZoneInfo(takvim.get("saat_dilimi", "Europe/Istanbul"))
    simdi = datetime.now(dilim)

    zamani_gelen = []
    for p in takvim["paylasimlar"]:
        if p.get("durum", "bekliyor") != "bekliyor":
            continue
        zaman = datetime.strptime(p["zaman"], "%Y-%m-%d %H:%M").replace(tzinfo=dilim)
        if zaman > simdi:
            continue
        if simdi - zaman > EN_FAZLA_GECIKME:
            print(f"ATLANDI  {p['id']}: zamanı {p['zaman']}, çok geç kalındı")
            if not kuru:
                p["durum"] = "atlandi"
            continue
        zamani_gelen.append(p)

    if not zamani_gelen:
        print("Zamanı gelen paylaşım yok.")
        if not kuru:
            yaz(takvim)
        return 0

    if not token and not kuru:
        print("IG_ACCESS_TOKEN tanımlı değil; kurulum tamamlanmamış.", file=sys.stderr)
        return 1

    kullanici = None
    hata_var = False
    for p in zamani_gelen:
        try:
            dogrula(p)
            if kuru:
                print(f"KURU     {p['id']}: {p['tur']} {p['medya']}")
                continue
            if kullanici is None:
                ben = istek("GET", "me", {"fields": "user_id,username"}, token)
                kullanici = ben.get("user_id") or ben["id"]
                print(f"Hesap: @{ben.get('username')}")
            medya_id = yayinla(p, kullanici, token)
            p.update(durum="yayinlandi", medya_id=medya_id,
                     yayin_zamani=datetime.now(dilim).strftime("%Y-%m-%d %H:%M"))
            p.pop("hata", None)
            print(f"YAYINDA  {p['id']}: {medya_id}")
        except (ApiHatasi, ValueError, OSError) as e:
            hata_var = True
            p["deneme"] = p.get("deneme", 0) + 1
            p["hata"] = str(e)
            if isinstance(e, ValueError) or p["deneme"] >= EN_FAZLA_DENEME:
                p["durum"] = "hata"
            print(f"HATA     {p['id']}: {e}", file=sys.stderr)

    if not kuru:
        yaz(takvim)
    return 1 if hata_var else 0


def yaz(takvim):
    with open(TAKVIM, "w", encoding="utf-8") as f:
        json.dump(takvim, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    sys.exit(main())
