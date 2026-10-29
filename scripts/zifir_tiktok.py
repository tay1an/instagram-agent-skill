#!/usr/bin/env python3
"""Zifir'in TikTok bağlantısı: giriş kodunu anahtara çevirir ve videoyu TikTok
gelen kutusuna taslak olarak yükler (Content Posting API, video.upload).

Kullanım:
  zifir_tiktok.py baglan <kod>    giriş kodundan yenileme anahtarı alır
  zifir_tiktok.py yukle <video>   videoyu taslak olarak gönderir
  zifir_tiktok.py takvim <takvim.json> <durum.json>
                                  zamanı gelen Instagram reel'ini TikTok'a taslak gönderir

Ortam: TT_KEY, TT_SECRET, TT_REFRESH (yukle için). Yeni yenileme anahtarı
YENI_REFRESH_DOSYASI'na yazılır; iş akışı onu ZIFIR_TT_REFRESH'e kaydeder.
"""

import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://open.tiktokapis.com/v2"
YONLENDIRME = "https://tay1an.github.io/zifirtiktok/tiktok-giris.html"
PARCA = 10 * 1024 * 1024
ONCE = datetime.timedelta(hours=10)  # TikTok gelen kutusu bildirimi saatlerce gecikebiliyor


class ApiHatasi(Exception):
    pass


def istek(yontem, url, govde=None, basliklar=None):
    req = urllib.request.Request(url, data=govde, method=yontem, headers=basliklar or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            veri = r.read()
    except urllib.error.HTTPError as e:
        veri = e.read()
        if not veri:
            raise ApiHatasi(f"HTTP {e.code}")
    return json.loads(veri) if veri else {}


def anahtar_al(alanlar):
    alanlar.update(client_key=os.environ["TT_KEY"].strip(), client_secret=os.environ["TT_SECRET"].strip())
    y = istek("POST", f"{API}/oauth/token/", urllib.parse.urlencode(alanlar).encode(),
              {"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in y:
        raise ApiHatasi(f"{y.get('error', '?')}: {y.get('error_description', y)}")
    for k in ("access_token", "refresh_token"):
        print(f"::add-mask::{y[k]}", flush=True)
    with open(os.environ["YENI_REFRESH_DOSYASI"], "w") as f:
        f.write(y["refresh_token"])
    print(f"İzinler: {y.get('scope')} · yenileme anahtarı {int(y.get('refresh_expires_in', 0)) // 86400} gün geçerli")
    return y["access_token"]


def api(yontem, yol, anahtar, govde):
    y = istek(yontem, f"{API}{yol}", json.dumps(govde).encode(),
              {"Authorization": f"Bearer {anahtar}", "Content-Type": "application/json; charset=UTF-8"})
    hata = y.get("error", {})
    if hata.get("code") not in (None, "ok"):
        raise ApiHatasi(f"{hata.get('code')}: {hata.get('message')}")
    return y.get("data", {})


def yukle(video):
    anahtar = anahtar_al({"grant_type": "refresh_token", "refresh_token": os.environ["TT_REFRESH"].strip()})
    boyut = os.path.getsize(video)
    parca = boyut if boyut <= 64 * 1024 * 1024 else PARCA
    adet = boyut // parca
    d = api("POST", "/post/publish/inbox/video/init/", anahtar, {"source_info": {
        "source": "FILE_UPLOAD", "video_size": boyut, "chunk_size": parca, "total_chunk_count": adet}})
    with open(video, "rb") as f:
        for i in range(adet):
            bas = i * parca
            son = boyut - 1 if i == adet - 1 else bas + parca - 1
            f.seek(bas)
            veri = f.read(son - bas + 1)
            req = urllib.request.Request(d["upload_url"], data=veri, method="PUT", headers={
                "Content-Type": "video/mp4", "Content-Length": str(len(veri)),
                "Content-Range": f"bytes {bas}-{son}/{boyut}"})
            with urllib.request.urlopen(req, timeout=300) as r:
                print(f"Parça {i + 1}/{adet}: HTTP {r.status}", flush=True)
    for _ in range(30):
        time.sleep(10)
        s = api("POST", "/post/publish/status/fetch/", anahtar, {"publish_id": d["publish_id"]})
        durum = s.get("status")
        print(f"Durum: {durum}", flush=True)
        if durum == "SEND_TO_USER_INBOX":
            print("Taslak TikTok gelen kutusunda: uygulamadaki bildirimden açıp paylaşabilirsin.")
            return d["publish_id"]
        if durum == "FAILED":
            raise ApiHatasi(f"yükleme başarısız: {s.get('fail_reason')}")
    raise ApiHatasi("durum 5 dakikada netleşmedi")


def takvim(takvim_yolu, durum_yolu):
    """Zamanına 10 saatten az kalmış ya da son 20 saatte zamanı gelmiş, TikTok'a
    henüz gitmemiş en eski reel'i ya da video hikâyeyi gönderir. Taslak erken gelir ki kullanıcı
    Instagram'la aynı saatte paylaşabilsin."""
    from zoneinfo import ZoneInfo
    t = json.load(open(takvim_yolu))
    simdi = datetime.datetime.now(ZoneInfo(t["saat_dilimi"])).replace(tzinfo=None)
    durum = json.load(open(durum_yolu)) if os.path.exists(durum_yolu) else {}
    for p in sorted(t["paylasimlar"], key=lambda p: p["zaman"]):
        zaman = datetime.datetime.strptime(p["zaman"], "%Y-%m-%d %H:%M")
        video = p["tur"] == "reel" or (p["tur"] == "hikaye" and p["medya"][0].endswith(".mp4"))
        if not video or p["id"] in durum or not simdi - datetime.timedelta(hours=20) <= zaman <= simdi + ONCE:
            continue
        print(f"Gönderiliyor: {p['id']}", flush=True)
        kayit = durum[p["id"]] = {"durum": "hata", "zaman": simdi.strftime("%Y-%m-%d %H:%M")}
        try:
            kayit["publish_id"] = yukle(p["medya"][0])  # hata olursa tekrar denenmez; kayıttan silinince yeniden gider
            kayit["durum"] = "gelen-kutusunda"
        finally:
            with open(durum_yolu, "w") as f:
                json.dump(durum, f, ensure_ascii=False, indent=2)
                f.write("\n")
        print("Açıklama (TikTok'ta yapıştırılacak):\n" + p.get("tiktok_aciklama", p.get("aciklama", "")))
        return
    print("Zamanı gelen yeni video yok.")


def main():
    komut, deger = sys.argv[1], sys.argv[2].strip()
    if komut == "baglan":
        anahtar_al({"grant_type": "authorization_code", "code": urllib.parse.unquote(deger),
                    "redirect_uri": YONLENDIRME})
        print("TikTok bağlandı.")
    elif komut == "takvim":
        takvim(deger, sys.argv[3])
    elif komut == "yukle":
        yukle(deger)
    else:
        raise SystemExit(f"bilinmeyen komut: {komut}")


if __name__ == "__main__":
    try:
        main()
    except ApiHatasi as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)
