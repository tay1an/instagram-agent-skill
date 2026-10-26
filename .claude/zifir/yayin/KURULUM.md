# Zifir: otomatik Instagram yayını kurulumu

@aziz.tahin için kurulan sistemin aynısı. `takvim.json` dosyasındaki
paylaşımlar zamanı gelince Zifir hesabında kendiliğinden yayınlanır. GitHub
her 15 dakikada bir kontrol eder.

Meta uygulaması ve GitHub'daki `GH_SECRETS_TOKEN` zaten var. Bu yüzden
kurulum yalnızca Zifir hesabını bağlamaktan ibaret ve 15-20 dakika sürer.
Bilgisayardan yapılması daha kolaydır.

> **Önemli:** Erişim anahtarını (token) hiçbir zaman sohbete yapıştırmayın.
> Yalnızca 3. adımda GitHub'daki gizli alana yapıştırın.

---

## 1. Zifir hesabını profesyonel hesap yapın

Instagram uygulamasında Zifir hesabına geçin → Profil → ☰ → Hesap türü ve
araçlar → **Profesyonel hesaba geç** → **İçerik üreticisi**. Hesap zaten
profesyonel hesapsa bu adımı atlayın.

## 2. Zifir hesabını Meta uygulamasına ekleyip erişim anahtarı alın

1. https://developers.facebook.com/apps adresinde, @aziz.tahin için
   kullandığınız uygulamayı açın.
2. **App roles → Roles → Instagram Testers → Add Instagram Testers** →
   Zifir hesabının kullanıcı adını yazın.
3. Zifir hesabıyla https://www.instagram.com/accounts/manage_access/
   adresini açın → **Tester davetleri** sekmesi → daveti **kabul edin**.
4. Uygulama panelinde **Instagram → API setup with Instagram login →
   Generate access tokens** → **Add account** → Zifir hesabıyla giriş
   yapıp izin verin.
5. Zifir hesabının yanındaki **Generate token** düğmesine basın ve çıkan
   uzun metni kopyalayın.

## 3. Anahtarı GitHub'a kaydedin

1. https://github.com/tay1an/instagram-agent-skill/settings/secrets/actions
2. **New repository secret**
3. Name: `IG_ACCESS_TOKEN_ZIFIR`, Secret: kopyaladığınız anahtar → **Add secret**

Anahtar her pazartesi kendiliğinden yenilenir. Bunun için ek bir şey
yapmanıza gerek yok, mevcut `GH_SECRETS_TOKEN` yeterli.

## 4. Deneyin

1. https://github.com/tay1an/instagram-agent-skill/actions → **Instagram yayın**
2. **Run workflow** → **Deneme** kutusunu işaretleyin → çalıştırın.
3. **"Zifir: zamanı gelen paylaşımları yayınla"** adımının kaydında
   `Bağlantı tamam: @<zifir kullanıcı adı>` ve `Paylaşım izni tamam`
   satırları görünmeli.

Kırmızı çarpı çıkarsa Claude'a haber verin.

---

## Takvim

| tarih (20:30) | video |
| --- | --- |
| 27 Ekim | 01-yabancilar |
| 28 Ekim | 03-ilk-cumle |
| 29 Ekim | 05-gece-iki |
| 30 Ekim | 04-fazlasi |
| 31 Ekim | 06-yakan-asklar |
| 1 Kasım | 02-hakli-miydim |
| 2 Kasım | 07-kimi-dusunerek |
| 3 Kasım | 08-kayboldum |
| 4 Kasım | uzak-lyric-dikey (lyric videonun tamamı) |

Bilmeniz gerekenler:

- Paylaşımlar 20:30-20:50 arasında çıkar.
- Kurulum bir paylaşımın saatinden sonra 3 saatten fazla gecikirse o
  paylaşım yayınlanmaz ("atlandi" olur). Claude'a söyleyin, tarihleri kaydırsın.
- API ile paylaşılan reel'lere Instagram müzik kütüphanesinden şarkı ve "AI
  ile oluşturuldu" etiketi eklenemez. Videolar şarkının kendi sesiyle çıkar.
- **TikTok bu sisteme dahil değil.** TikTok'un API'si denetimden geçmemiş
  uygulamaların paylaşımlarını yalnızca "gizli" yayınlıyor. TikTok için
  tiktok.com/upload adresindeki "Zamanla" seçeneğini kullanın.
- Depo herkese açık olduğu için videolar ve açıklamalar yayın saatinden önce
  GitHub'da görülebilir.
