"""27 Ekim-10 Kasım planının üretim listesi: (id, tür, tarih saat, foto, filtre, mx, zoom, my, t0, kapak sözü)."""
S = "stok/"
REEL = [  # 4-10 Kasım fotoğraflı yeni reel'ler (20:30)
    ("09-sevgili", "2026-11-04", S + "07-sahil.jpg", "gunbatimi", 0.5, 1.0, 0.5, 102.9, "Sevgili sevgilim dünüm yarınım"),
    ("10-sabah", "2026-11-05", S + "05-iskele.jpg", "lila", 0.5, 1.2, 0.5, 111.0, "Bir sabah var hep uyanmak isterim"),
    ("11-kor-yara", "2026-11-06", S + "08-sis.jpg", "kalp", 0.6, 1.3, 0.62, 12.5, "Kor yara sol yanım deşme dur daha"),
    ("12-kokler", "2026-11-07", S + "03-eller.jpg", "agac", 0.45, 1.0, 0.5, 65.8, "Köklerini versene"),
    ("13-kalbim", "2026-11-08", S + "02-sehir.jpg", "sicak-yagmur", 0.5, 1.0, 0.5, 114.9, "Kalbim yerinde yanımda senin yerin"),
    ("14-yuk", "2026-11-09", S + "07-sahil.jpg", "gece", 0.5, 1.2, 0.6, 126.9, "Yük olur her yudum içe işledikçe"),
    ("15-oysa", "2026-11-10", S + "08-sis.jpg", "yagmur", 0.5, 1.0, 0.5, 138.3, "Oysa seni sana anlatan ben idim"),
]
HIKAYE = [  # 15 sn şarkılı hikâyeler (13:00); aynı günün reel'iyle aynı kısmı kullanmaz
    ("v01-yuk-olur", "2026-10-27", S + "05-iskele.jpg", "gece", 0.5, 1.4, 0.55, 47.1),
    ("v02-kor-yara", "2026-10-28", S + "03-eller.jpg", "kalp", 0.5, 1.6, 0.62, 12.5),
    ("v03-keyfine", "2026-10-29", S + "02-sehir.jpg", "mum", 0.7, 1.3, 0.45, 27.8),
    ("v04-sevgili", "2026-10-30", S + "08-sis.jpg", "gece", 0.4, 1.0, 0.5, 102.9),
    ("v05-oktur", "2026-10-31", S + "07-sahil.jpg", "yagmur", 0.5, 1.2, 0.6, 16.3),
    ("v06-kokler", "2026-11-01", S + "03-eller.jpg", "agac", 0.45, 1.0, 0.5, 145.1),
    ("v07-sabah", "2026-11-02", S + "05-iskele.jpg", "lila", 0.5, 1.0, 0.5, 111.0),
    ("v08-ufuk", "2026-11-03", S + "02-sehir.jpg", "sicak-yagmur", 0.45, 1.0, 0.5, 123.1),
    ("v09-parcalar", "2026-11-04", S + "08-sis.jpg", "kalp", 0.6, 1.3, 0.62, 19.9),
    ("v10-olmayi", "2026-11-05", S + "07-sahil.jpg", "gunbatimi", 0.5, 1.0, 0.5, 31.6),
    ("v11-ozune", "2026-11-06", S + "08-sis.jpg", "lila", 0.6, 1.3, 0.62, 54.1),
    ("v12-ardinda", "2026-11-07", S + "05-iskele.jpg", "agac", 0.5, 1.4, 0.55, 50.9),
    ("v13-ben-eger", "2026-11-08", S + "02-sehir.jpg", "gece", 0.55, 1.15, 0.55, 62.4),
    ("v14-elindeki", "2026-11-09", S + "03-eller.jpg", "kalp", 0.5, 1.3, 0.6, 8.7),
    ("v15-ustume", "2026-11-10", S + "07-sahil.jpg", "lila", 0.5, 1.0, 0.5, 107.3),
]
