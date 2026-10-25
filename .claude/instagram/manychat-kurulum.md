# ManyChat kurulumu: yoruma TAHİN yazana otomatik tarif

Yorumlara "TAHİN" yazan herkese ManyChat otomatik olarak DM gönderir.
ManyChat, Meta'nın resmi iş ortağıdır; Instagram'ın izin verdiği yoldan çalışır.
Kurulum bir kez yapılır, yaklaşık 15 dakika sürer. Bilgisayardan yapmak daha
kolaydır. ManyChat ekranları zaman zaman değişir; bir adım farklı görünürse
ekran görüntüsünü Claude'a gönderin.

## 1. Hesap açın ve Instagram'ı bağlayın

1. https://manychat.com adresine gidin, **Get Started Free** deyin.
2. **Instagram**'ı seçin ve @aziz.tahin ile giriş yapıp izin verin.
3. Instagram'da şu ayar açık olmalı: Ayarlar → Mesajlar ve hikâye yanıtları →
   Mesaj kontrolleri → Bağlı araçlar → **Mesajlara erişime izin ver**.

## 2. Otomasyonu oluşturun

1. Sol menüden **Automation** → **New Automation** (ya da **Templates**
   içinden "Auto-DM from comments" benzeri bir şablon).
2. Tetikleyici (trigger): **User comments on your Post or Reel**.
   - **Which Post or Reel:** Any Post or Reel (tüm gönderiler).
   - **Keywords:** şu dört kelimeyi ekleyin: `tahin`, `Tahin`, `TAHİN`, `TAHIN`
   - **Reply to their comments under the post:** açık. Cevap olarak
     şunları ekleyin (ManyChat sırayla kullanır):
     - `DM'den yazdık 🤎`
     - `Mesajlarınıza bakın 🤎`
     - `Tarifler DM'de sizi bekliyor 🥄`
3. İlk DM (Opening DM) metni:

```
Merhaba, ilginiz için teşekkür ederiz! 🤎 Aziz Tahin ile hazırladığımız 5 tarif hazır. Aşağıdaki düğmeye basmanız yeterli.
```

   Düğme (button) metni: `Tarifleri gönder`

4. Düğmeye basılınca gönderilecek mesajlar: düğmeye bağlı yeni bir
   **Instagram > Send Message** adımı ekleyin ve aşağıdaki mesajları **ayrı
   ayrı metin blokları** olarak sırayla ekleyin. Her biri Instagram'ın 1000
   karakter sınırının altındadır.

**Mesaj 1** (129 karakter)

```
Merhaba, ilginiz için teşekkür ederiz! 🤎 Aziz Tahin ürünleriyle evde kolayca
yapabileceğiniz 5 tarifimizi aşağıda bulabilirsiniz.
```

**Mesaj 2** (309 karakter)

```
1. Bademli Tahin Soslu Tavuk (Hazırlama 30 dk, pişirme 30 dk, 4-5 kişilik)

Malzemeler:
- 800 gr tavuk bonfile
- 50 gr soyulmuş badem
- 1 orta boy soğan
- 3 adet havuç
- Yarım çay bardağı zeytinyağı
- Karabiber
- Tuz

Sosu için:
- 1 su bardağı Aziz Tahin
- 2 adet orta boy limonun suyu
- 100 gr soyulmuş badem
```

**Mesaj 3** (755 karakter)

```
Yapılışı:
1. 100 gr bademi 1 su bardağı su ile iyice öğütüp elde edilen karışımdan badem sütünü süzün.
2. Kalan 50 gr bademi, yarım çay bardağı zeytinyağında 3-4 dk kavurun. Sonrasında küp doğranmış kuru soğanları ve yuvarlak dilimlenmiş havuçları ekleyip kavurmaya devam edin.
3. Ardından kuşbaşı doğranmış tavuk bonfileyi ilave edip üzerine bol karabiber ve isteğe göre tuz ekleyip tavuklar iyice kızarana kadar arada karıştırarak pişirin.
4. Bu sırada sosu için 1 su bardağı Aziz Tahin, 2 orta boy limon suyunu ve hazırlanan badem sütünü birlikte yavaşça çırpıp iyice karıştırın.
5. Tavuklar kızardıktan sonra, elde ettiğiniz tahinli badem sütlü sosu yavaşça üzerine ekleyin.
6. Yaklaşık 4-5 dk daha kısık ateşte pişirdikten sonra servis edebilirsiniz.
```

**Mesaj 4** (493 karakter)

```
2. Tahinli Cevizli Milföy Rulo

Malzemeler:
- 1 su bardağı Aziz Tahin
- Milföy
- 2 yemek kaşığı sıvı yağ
- Çekilmiş ceviz
- 3/4 su bardağı pudra şekeri

Yapılışı:
1. Milföyleri tepsiye dizip şeritler halinde kesin.
2. Tahin, sıvı yağ ve pudra şekerini karıştırın.
3. Karışımı şeritler halinde kesilmiş milföylerin üzerine sürüp ceviz ekleyin ve şeritleri rulo yapın.
4. Ruloları tepsiye dizip üzerlerine biraz daha tahinli karışım ve ceviz ekleyin.
5. 200°C fırında yaklaşık 25 dakika pişirin.
```

**Mesaj 5** (589 karakter)

```
3. Ev Yapımı Humus

Malzemeler:
- 2 su bardağı haşlanmış nohut
- Yarım su bardağı Aziz Tahin
- Yarım çay bardağı Aziz Zeytinyağı
- 1 limonun suyu
- 2 diş sarımsak
- 1-2 yemek kaşığı soğuk su
- Tuz, kimyon
- Üzeri için 1-2 yemek kaşığı Aziz Zeytinyağı ve kırmızı biber

Yapılışı:
1. Nohut, tahin, zeytinyağı, limon suyu, sarımsak, tuz ve kimyonu mutfak robotuna alın.
2. Soğuk suyu ekleyerek 3-4 dakika, pürüzsüz olana kadar çekin.
3. Tabağa yayın, üzerine 1-2 yemek kaşığı Aziz Zeytinyağı gezdirip kırmızı biber serpin. Susam aromasını sevenler birkaç damla Aziz Tahin Yağı da ekleyebilir.
```

**Mesaj 6** (529 karakter)

```
4. Tahinli Ballı Enerji Topları (yaklaşık 12 adet, fırın gerekmez)

Malzemeler:
- 1 su bardağı yulaf
- 3 yemek kaşığı Aziz Tahin
- 2 yemek kaşığı Aziz %100 doğal Ovacık Balı
- Yarım çay bardağı çekilmiş ceviz ya da fındık
- 1 yemek kaşığı kakao (isteğe bağlı)
- Bir tutam tuz
- Üzeri için susam

Yapılışı:
1. Tüm malzemeleri bir kapta iyice karıştırın.
2. Karışımdan ceviz büyüklüğünde parçalar alıp yuvarlayın, susama bulayın.
3. Buzdolabında 30 dakika dinlendirin. Spor sonrası ya da ara öğünde tok tutan bir atıştırmalık olur.
```

**Mesaj 7** (358 karakter)

```
5. Ballı Tahin

Malzemeler:
- 3 yemek kaşığı Aziz Tahin
- 1 yemek kaşığı Aziz %100 doğal Ovacık Balı
- Tarçın (isteğe göre)

Yapılışı:
1. Tahini kavanozda iyice karıştırın; doğal tahinin yağı üste çıkar, bu katkısız olduğunun işaretidir.
2. Tahin ve balı küçük bir kasede karıştırın. İsterseniz üzerine tarçın serpin.
3. Taze ekmekle kahvaltı sofranıza alın.
```

**Mesaj 8** (203 karakter)

```
Afiyet olsun! 🥄 Tariflerde kullandığımız tahin, Ovacık balı, zeytinyağı ve tahin
yağını sipariş etmek için profilimizdeki WhatsApp linkinden bize
yazabilirsiniz. Türkiye'nin her iline gönderim yapıyoruz.
```

5. Sağ üstten **Set Live** (Yayına al) deyin.

## 3. Deneyin

Başka bir hesaptan son gönderilerinizden birine `TAHİN` yazın. Birkaç saniye
içinde DM gelmeli; düğmeye basınca tarifler gelmeli.

## Notlar

- Ücretsiz plan başlangıç için yeterlidir. Kişi sayısı sınırı aşılırsa ManyChat
  ücretli plana geçmeyi önerir.
- Tarif listesi değişirse bu dosyadaki mesajları ManyChat'te de güncelleyin.
- Bizim GitHub'daki eski otomatik yorum sistemi kapatıldı; iki sistem aynı
  kişiye iki kez mesaj atmaz.
