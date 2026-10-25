#!/usr/bin/env python3
"""Yorumlara "TAHİN" yazanlara tarif listesini DM ile gönderir.

GitHub Actions tarafından instagram_yayinla.py ile aynı aralıkta çalıştırılır.
İki aşamalıdır, çünkü Instagram bir yoruma yalnızca tek bir özel yanıt
gönderilmesine izin verir ve mesajlar 1000 karakterle sınırlıdır:

  1. Son gönderilerdeki yorumlar taranır. Yalnızca "tahin" yazan (büyük/küçük
     harf, İ/i, noktalama fark etmez) her yoruma bir kez özel yanıt gider:
     "tarifler için Evet yazın". Yoruma herkese açık kısa bir cevap da yazılır.
  2. Özel yanıta cevap veren kişiye (konuşma açıldığı için) tarifler birkaç
     mesaj hâlinde gönderilir.

Durum, aynı yorumun iki kez işlenmemesi için bir JSON dosyasında tutulur. Depo
herkese açık olduğundan bu dosya depoya yazılmaz; iş akışı onu GitHub
Actions önbelleğinde saklar. Kullanıcı adı saklanmaz, kayıtlar 30 gün sonra
silinir (bkz. docs/gizlilik.html).

Ortam değişkenleri: IG_ACCESS_TOKEN, isteğe bağlı IG_API_VERSION,
KURU_CALISMA=1 (hiçbir şey göndermez, yalnızca ne yapılacağını yazar).
"""

import json
import os
import random
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from instagram_yayinla import ApiHatasi, istek  # noqa: E402

DURUM = os.environ.get("YORUM_DURUMU", ".yorum-durumu/durum.json")
SAKLAMA_SURESI = timedelta(days=30)
TARIFLER = os.environ.get("TARIF_LISTESI", ".claude/instagram/tarif-listesi.md")

ANAHTARLAR = {"tahin", "tahın"}  # İngilizce klavyede "TAHIN" yazanlar için
TARANACAK_GONDERI = 10
OZEL_YANIT_SURESI = timedelta(days=7)  # Instagram sınırı
KONUSMA_SURESI = timedelta(hours=24)  # kişinin son mesajından sonra
EN_FAZLA_MESAJ = 1000

OZEL_YANIT = (
    "Merhaba, ilginiz için teşekkür ederiz! 🤎 Aziz Tahin ile hazırladığımız "
    "5 tarif hazır. Hemen göndermemiz için bu mesaja \"Evet\" yazmanız yeterli."
)
HERKESE_ACIK_YANITLAR = [
    "DM'den yazdık 🤎",
    "Mesajlarınıza bakın 🤎",
    "Tarifler DM'de sizi bekliyor 🥄",
]


def normalize(metin):
    metin = metin.replace("İ", "i").replace("I", "ı").lower()
    return re.sub(r"[^\wçğıöşü ]", " ", metin).split()


def anahtar_mi(metin):
    """Yorum yalnızca anahtar kelimeden ibaretse (en fazla 3 kelime) True."""
    kelimeler = normalize(metin or "")
    return bool(ANAHTARLAR & set(kelimeler)) and len(kelimeler) <= 3


def tarif_mesajlari(yol=TARIFLER):
    """tarif-listesi.md dosyasını 1000 karakteri aşmayan mesajlara böler."""
    metin = open(yol, encoding="utf-8").read().split("---", 1)[1]
    govde, kapanis = metin.rsplit("\n---\n", 1)
    giris, tarifler = govde.split("**1. ", 1)
    parcalar = re.split(r"\n(?=\*\*\d\. )", ("**1. " + tarifler).strip())

    def temizle(t):
        t = t.replace("**", "")
        return re.sub(r"\n +", " ", t).strip()

    mesajlar = [temizle(giris)]
    for p in parcalar:
        p = temizle(p)
        if len(p) <= EN_FAZLA_MESAJ:
            mesajlar.append(p)
        else:
            bas, son = p.split("\nYapılışı:", 1)
            mesajlar += [bas.strip(), "Yapılışı:" + son]
    mesajlar.append(temizle(kapanis))
    for m in mesajlar:
        if len(m) > EN_FAZLA_MESAJ:
            raise ValueError(f"mesaj {len(m)} karakter: {m[:40]}...")
    return mesajlar


def zaman(s):
    return datetime.strptime(s.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")


def simdi():
    return datetime.now(timezone.utc)


def mesaj_gonder(alici, metin, token):
    return istek("POST", "me/messages", {
        "recipient": json.dumps(alici),
        "message": json.dumps({"text": metin}, ensure_ascii=False),
    }, token)


def yorumlari_tara(durum, ben, token, kuru):
    gonderiler = istek("GET", f"{ben}/media", {"fields": "id,timestamp,comments_count", "limit": TARANACAK_GONDERI}, token)
    ozet = {"gonderi": 0, "yorum": 0, "eslesen": 0, "kimliksiz": 0}
    for g in gonderiler.get("data", []):
        if simdi() - zaman(g["timestamp"]) > timedelta(days=30):
            continue
        ozet["gonderi"] += 1
        yorumlar = istek("GET", f"{g['id']}/comments", {"fields": "id,text,timestamp,from", "limit": 50}, token)
        veri = yorumlar.get("data", [])
        print(f"Gönderi {g['timestamp'][:10]}: Instagram'a göre {g.get('comments_count')} yorum, okunan {len(veri)}")
        ozet["yorum"] += len(veri)
        for y in veri:
            if anahtar_mi(y.get("text")):
                ozet["eslesen"] += 1
                if not (y.get("from") or {}).get("id"):
                    ozet["kimliksiz"] += 1
            onceki = durum["yorumlar"].get(y["id"])
            if onceki and (onceki["durum"] != "hata" or onceki.get("deneme", 1) >= 3):
                continue
            if not anahtar_mi(y.get("text")):
                continue
            kimden = (y.get("from") or {}).get("id")
            if not kimden or kimden == ben:
                continue
            if simdi() - zaman(y["timestamp"]) > OZEL_YANIT_SURESI:
                continue
            if kuru:
                print(f"KURU     yorum {y['id']}: özel yanıt gönderilecek")
                continue
            kayit = {"kisi": kimden, "zaman": simdi().isoformat(timespec="seconds")}
            try:
                mesaj_gonder({"comment_id": y["id"]}, OZEL_YANIT, token)
                kayit["durum"] = "ozel_yanit"
                print(f"YANIT    yorum {y['id']}: özel yanıt gönderildi")
            except ApiHatasi as e:
                deneme = (onceki or {}).get("deneme", 0) + 1
                kayit.update(durum="hata", hata=str(e), deneme=deneme)
                print(f"HATA     yorum {y['id']}: {e}", file=sys.stderr)
            durum["yorumlar"][y["id"]] = kayit
            if kayit["durum"] == "ozel_yanit":
                try:
                    istek("POST", f"{y['id']}/replies", {"message": random.choice(HERKESE_ACIK_YANITLAR)}, token)
                except ApiHatasi as e:
                    print(f"UYARI    yorum {y['id']}: herkese açık yanıt yazılamadı: {e}", file=sys.stderr)
    print(f"Özet: {ozet['gonderi']} gönderi, {ozet['yorum']} yorum, {ozet['eslesen']} TAHİN yorumu"
          + (f" ({ozet['kimliksiz']} tanesinde yazan kişinin kimliği gelmedi)" if ozet["kimliksiz"] else ""))


def cevap_verdi_mi(kisi, sonra, token):
    """Kişi, özel yanıttan sonra bize mesaj attıysa son mesajının zamanını döndürür."""
    k = istek("GET", "me/conversations", {
        "platform": "instagram", "user_id": kisi,
        "fields": "messages.limit(10){from,created_time}",
    }, token)
    en_son = None
    for konusma in k.get("data", []):
        for m in konusma.get("messages", {}).get("data", []):
            if (m.get("from") or {}).get("id") == kisi:
                t = zaman(m["created_time"])
                if t > sonra and (en_son is None or t > en_son):
                    en_son = t
    return en_son


def tarifleri_gonder(durum, token, kuru):
    mesajlar = None
    for yorum_id, kayit in durum["yorumlar"].items():
        if kayit.get("durum") != "ozel_yanit":
            continue
        gonderim = datetime.fromisoformat(kayit["zaman"])
        if simdi() - gonderim > OZEL_YANIT_SURESI:
            kayit["durum"] = "cevapsiz"
            continue
        try:
            son = cevap_verdi_mi(kayit["kisi"], gonderim, token)
        except ApiHatasi as e:
            print(f"HATA     yorum {yorum_id}: konuşma okunamadı: {e}", file=sys.stderr)
            continue
        if not son or simdi() - son > KONUSMA_SURESI:
            continue
        if kuru:
            print(f"KURU     yorum {yorum_id}: tarifler gönderilecek")
            continue
        mesajlar = mesajlar or tarif_mesajlari()
        try:
            for m in mesajlar:
                mesaj_gonder({"id": kayit["kisi"]}, m, token)
            kayit.update(durum="tarif_gonderildi", tarif_zamani=simdi().isoformat(timespec="seconds"))
            print(f"TARİF    yorum {yorum_id}: {len(mesajlar)} mesaj gönderildi")
        except ApiHatasi as e:
            kayit["hata"] = str(e)
            print(f"HATA     yorum {yorum_id}: tarifler gönderilemedi: {e}", file=sys.stderr)


def main():
    kuru = os.environ.get("KURU_CALISMA") == "1"
    token = os.environ.get("IG_ACCESS_TOKEN")
    tarif_mesajlari()  # dosya bozuksa hiçbir şey göndermeden dur
    if not token:
        print("IG_ACCESS_TOKEN tanımlı değil; atlandı.")
        return 0
    try:
        durum = json.load(open(DURUM, encoding="utf-8"))
    except FileNotFoundError:
        durum = {"yorumlar": {}}
    durum["yorumlar"] = {
        k: v for k, v in durum["yorumlar"].items()
        if simdi() - datetime.fromisoformat(v["zaman"]) <= SAKLAMA_SURESI
    }
    ben = istek("GET", "me", {"fields": "user_id"}, token)
    ben = ben.get("user_id") or ben["id"]
    try:
        yorumlari_tara(durum, ben, token, kuru)
        tarifleri_gonder(durum, token, kuru)
    finally:
        if not kuru:
            os.makedirs(os.path.dirname(DURUM) or ".", exist_ok=True)
            with open(DURUM, "w", encoding="utf-8") as f:
                json.dump(durum, f, ensure_ascii=False, indent=2)
                f.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ApiHatasi as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)
