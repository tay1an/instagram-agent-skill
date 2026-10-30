"""27 Ekim kullanıcı isteği:
- Çapa söz grubu dört satırın tamamıyla, her 3-4 günde bir, her seferinde farklı görselle:
  "Oysa seni sana anlatan ben idim / Ben eğer yok isem sen de olmazsın dedim /
   Yan yana ağacız gölge yeter bize / Köklerini versene" (1. nakarat, 58.6-73.6 sn).
- Her reel kapağında insan görünür.
- Uzun video: ikinci kıta + nakarat (dikey lyric videodan 103.0-157.0 sn).
"""
S = "stok/"
CAPA_ACIKLAMA = ("\"oysa seni sana anlatan ben idim\nben eğer yok isem sen de olmazsın dedim\n"
                 "yan yana ağacız gölge yeter bize\nköklerini versene\"")
CAPA_KAPAK = "Oysa seni sana anlatan ben idim. Ben eğer yok isem sen de olmazsın dedim"
CAPA = [  # (ad, tarih, foto, filtre, mx, zoom, my, t0, süre)
    ("16-capa-sahil", "2026-11-04", S + "07-sahil.jpg", "sicak-yagmur", 0.5, 1.0, 0.5, 58.6, 15.0),
    ("17-capa-iskele", "2026-11-07", S + "05-iskele.jpg", "yagmur", 0.5, 1.4, 0.55, 58.6, 15.0),
    # Kullanıcının kendi fotoğrafı (28 Ekim): insan yok, kapak 03-eller'den ("Yan yana ağacız gölge yeter bize", lila).
    ("19-capa-lamba", "2026-11-14", S + "09-lamba.jpg", "dogal", 0.5, 1.0, 0.5, 58.6, 15.0),
]
UZUN = ("18-kita2", "2026-11-08", 103.0, 157.0, S + "05-iskele.jpg", "lila", 0.5, 1.4, 0.55,
        "Sevgili sevgilim dünüm yarınım", "\"sevgili sevgilim dünüm yarınım\"\nikinci kıta ve nakarat, baştan sona.")
TASINAN = {"09-sevgili": "2026-11-11", "12-kokler": "2026-11-12", "13-kalbim": "2026-11-13"}
HIKAYE = [  # 11-13 Kasım hikâyeleri (18:00)
    ("v16-alev", "2026-11-11", S + "07-sahil.jpg", "mum", 0.5, 1.2, 0.6, 23.7),
    ("v17-ufuk", "2026-11-12", S + "03-eller.jpg", "gece", 0.5, 1.3, 0.6, 43.4),
    ("v18-vardim", "2026-11-13", S + "08-sis.jpg", "gunbatimi", 0.6, 1.3, 0.62, 35.2),
    ("v19-lamba", "2026-11-14", S + "09-lamba.jpg", "dogal", 0.55, 1.1, 0.56, 23.7),
]
# 30 Ekim kullanıcı isteği: "Sevgili sevgilim" kıtasının tamamı, 15 Kasım; kapak yazısız (08-sis, gece, figür yakın).
KITA = ("20-sevgili-kita", "2026-11-15", S + "08-sis.jpg", "gece", 0.4, 1.0, 0.5, 102.9, 20.6)
