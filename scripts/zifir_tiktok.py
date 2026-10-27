#!/usr/bin/env python3
"""Zifir'in TikTok bağlantısı: giriş kodunu anahtara çevirir ve videoyu TikTok
gelen kutusuna taslak olarak yükler (Content Posting API, video.upload).

Kullanım:
  zifir_tiktok.py baglan <kod>    giriş kodundan yenileme anahtarı alır
  zifir_tiktok.py yukle <video>   videoyu taslak olarak gönderir

Ortam: TT_KEY, TT_SECRET, TT_REFRESH (yukle için). Yeni yenileme anahtarı
YENI_REFRESH_DOSYASI'na yazılır; iş akışı onu ZIFIR_TT_REFRESH'e kaydeder.
"""

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
            return
        if durum == "FAILED":
            raise ApiHatasi(f"yükleme başarısız: {s.get('fail_reason')}")
    raise ApiHatasi("durum 5 dakikada netleşmedi")


def main():
    komut, deger = sys.argv[1], sys.argv[2].strip()
    if komut == "baglan":
        anahtar_al({"grant_type": "authorization_code", "code": urllib.parse.unquote(deger),
                    "redirect_uri": YONLENDIRME})
        print("TikTok bağlandı.")
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
