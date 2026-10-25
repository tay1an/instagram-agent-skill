# Otomatik Instagram yayını: kurulum

Bu sistem, `takvim.json` dosyasına yazılan paylaşımları zamanı gelince
@aziz.tahin hesabında kendiliğinden yayınlar. Her 15 dakikada bir GitHub
üzerinde çalışır; bilgisayarınızın açık olması gerekmez.

Kurulum bir kez yapılır, yaklaşık 30-60 dakika sürer. Bilgisayardan yapılması
daha kolaydır. Meta'nın menü adları zaman zaman değişir; bir adım burada
yazdığı gibi görünmezse ekran görüntüsünü Claude'a gönderin.

> **Önemli:** Erişim anahtarını (token) hiçbir zaman sohbete yapıştırmayın.
> Yalnızca 3. adımda GitHub'daki gizli alana yapıştırın.

---

## 1. Instagram hesabını işletme hesabı yapın

Instagram uygulaması → Profil → ☰ → Hesap türü ve araçlar → **Profesyonel
hesaba geç** → **İşletme**. Hesap zaten işletme hesabıysa bu adımı atlayın.

## 2. Meta'da uygulama oluşturup erişim anahtarı alın

1. https://developers.facebook.com adresine Facebook hesabınızla girin.
   İlk kez giriyorsanız geliştirici olarak kaydolmanız istenir (ücretsiz).
2. **Uygulamalarım → Uygulama oluştur**.
3. Kullanım durumu olarak **"Instagram'da mesajları ve içeriği yönet"**
   (Manage messaging & content on Instagram) seçeneğini seçin. Uygulamaya
   "Aziz Tahin Yayın" gibi bir ad verin.
4. Uygulama panelinde **Instagram → Instagram girişiyle API kurulumu**
   (API setup with Instagram login) bölümüne gidin.
5. **Erişim anahtarları oluştur** (Generate access tokens) başlığında
   **Hesap ekle**'ye basın ve @aziz.tahin ile giriş yapıp izin verin.
6. Hesabın yanında çıkan **Anahtar oluştur** (Generate token) düğmesine
   basın. Çıkan uzun metni kopyalayın. Bu sizin erişim anahtarınız.

## 3. Anahtarı GitHub'a kaydedin

1. https://github.com/tay1an/instagram-agent-skill/settings/secrets/actions
   adresini açın.
2. **New repository secret**'a basın.
3. Name: `IG_ACCESS_TOKEN`, Secret: kopyaladığınız anahtar. **Add secret**.

## 4. Anahtarın kendini yenilemesini sağlayın

Instagram anahtarı 60 günde sona erer. Sistem her pazartesi anahtarı
kendiliğinden yeniler, ama bunun için GitHub'a bir izin vermeniz gerekir:

1. https://github.com/settings/personal-access-tokens/new adresini açın.
2. Token name: `instagram anahtar yenileme`. Expiration: **No expiration**
   ya da en uzun süre.
3. Repository access: **Only select repositories** →
   `tay1an/instagram-agent-skill`.
4. Permissions → Repository permissions → **Secrets: Read and write**.
5. **Generate token**, çıkan metni kopyalayın.
6. 3. adımdaki sayfada yeni bir secret ekleyin: Name `GH_SECRETS_TOKEN`,
   Secret: bu metin.

## 5. Deneyin

1. https://github.com/tay1an/instagram-agent-skill/actions adresinde
   **Instagram yayın**'a tıklayın.
2. **Run workflow**'a basın, **Deneme** kutusunu işaretleyin, çalıştırın.
   Bu hiçbir şey paylaşmaz, yalnızca sistemin çalıştığını gösterir.
3. **Instagram anahtar yenileme**'yi de bir kez **Run workflow** ile
   çalıştırın. Yeşil tik çıkarsa kurulum tamam.

Kırmızı çarpı çıkarsa Claude'a haber verin.

---

## Kullanım

Kurulumdan sonra Claude'a "şu görseli yarın 09:00'da hikâye olarak paylaş"
demeniz yeterli. Claude görseli hazırlar, takvime ekler ve kaydeder; zamanı
gelince sistem paylaşır.

Bilmeniz gerekenler:

- Paylaşımlar 15 dakikalık kontrollerle çıkar; GitHub yoğunken 5-20 dakika
  gecikebilir. 09:00 hikâyesi 09:00-09:20 arasında çıkar.
- 3 saatten fazla gecikmiş bir paylaşım yayınlanmaz ("atlandi" olur), sabah
  hikâyesi akşam çıkmasın diye.
- **Anket, test, soru kutusu gibi çıkartmalar API ile eklenemez.** Bunlar
  olan hikâyeler takvime "taslak" olarak yazılır ve elle paylaşılır.
- Görseller JPG, videolar MP4 olmalı. Claude bunu kendisi ayarlar.
- Depo herkese açık olduğu için takvimdeki görseller ve metinler yayın
  saatinden önce de GitHub'da görülebilir. Erişim anahtarı ise gizli
  alanda durduğu için görünmez.

## Takvim dosyasının yapısı

`takvim.json` içindeki her paylaşım:

| alan | anlamı |
| --- | --- |
| `id` | benzersiz ad, ör. `2026-10-26-hikaye-sabah` |
| `tur` | `hikaye`, `gonderi`, `reel` ya da `carousel` |
| `zaman` | Türkiye saatiyle `YYYY-AA-GG SS:DD` |
| `medya` | dosya yolları; carousel için 2-10 dosya |
| `aciklama` | gönderi açıklaması (hikâyede kullanılmaz) |
| `kapak` | reel kapağı (isteğe bağlı) |
| `durum` | `bekliyor`, `taslak`, `yayinlandi`, `atlandi`, `hata` |

Sistem yayınladıktan sonra `durum`, `medya_id` ve `yayin_zamani` alanlarını
kendisi doldurur.
