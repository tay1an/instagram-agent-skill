# Otomatik paylaşım: olası sorunlar ve önlemler

Paylaşımlar şu zincirle çıkar: **takvim.json → GitHub Actions (Instagram yayın
iş akışı) → Meta uygulaması (AzizTahin) → Instagram API**. Zincirin herhangi
bir halkası koparsa paylaşım çıkmaz. Aşağıda yaşanmış ve yaşanabilecek
sorunlar, nedenleri ve alınan önlemler var.

## Bekçi (her gün otomatik kontrol)

Claude her gün 09:25, 12:50, 19:25 ve 21:25'te (Türkiye saati) takvime bakar:
zamanı geçmiş ama "bekliyor" ya da "hata" kalan paylaşım var mı? Varsa nedeni
bulur, düzeltebiliyorsa düzeltip paylaştırır; düzeltemiyorsa görseli ve
açıklamayı elle paylaşım için kullanıcıya gönderir ve takvimde "elle" yapar
(sistem açılınca ikinci kez paylaşmasın). Sorun yoksa kimseye yazmaz.

## Sorunlar

| # | sorun | belirti | neden | önlem / çözüm |
| --- | --- | --- | --- | --- |
| 1 | **Actions kapalı** (28 Ekim) | hiçbir paylaşım çıkmaz, e-posta da gelmez | depo ayarında "Disable actions" seçildi ya da GitHub kapattı | Bekçi fark eder. Çözüm: Settings → Actions → General → "Allow all actions…" → Save. Ayar doğruysa ve yine kapalıysa GitHub kapatmıştır: github.com/contact |
| 2 | **Meta API engeli** (26 Ekim) | "API access blocked" | anahtar bozuldu / kısa sürede çok deneme (aynı uygulamada iki hesap) | Yeni anahtar: Meta → Use cases → API setup → Generate token → GitHub sırrı IG_ACCESS_TOKEN. Başarısız paylaşımı art arda elle denemeyin. |
| 3 | **Çift paylaşım** (27 Ekim) | aynı hikâye iki kez | sıradaki iş eski takvimi okudu | Düzeltildi: iş dalın en son halini alır, bekledikten sonra takvimi yeniden okur. |
| 4 | **Durum kaydı çakışması** | "Run failed" e-postası, sonra çift paylaşım riski | başka bir oturum aynı anda takvimi değiştirdi | Düzeltildi: yalnızca değişen paylaşımlar en son takvime uygulanır, 5 kez denenir; her paylaşımdan hemen sonra kaydedilir. |
| 5 | **Gecikme** (26 Ekim) | 12:30 paylaşımı 12:52'de | GitHub zamanlayıcısı yoğunken saatte bir çalışıyor | Düzeltildi: iş 70 dakika içindeki paylaşımı bekleyip tam dakikasında yayınlar. 3 saatten fazla gecikene "atlandi" denir. |
| 6 | **Geçici Instagram hatası** | "does not exist", "not ready" | yeni medya kabı birkaç saniye hazır olmuyor | Kısa bekleyip yeniden dener; iş başına en fazla 3 deneme. |
| 7 | **Anahtar süresi** | "Session has expired", "Invalid OAuth" | Instagram anahtarı 60 günde biter | "Instagram anahtar yenileme" her pazartesi yeniler. Yenilemeyi yapan GH_SECRETS_TOKEN **1 Haziran 2027**'de biter; ondan önce GitHub'da yenisi oluşturulup sırra yazılmalı. |
| 8 | **Depo gizli yapılırsa** | "media could not be fetched" | görseller raw.githubusercontent.com adresinden herkese açık okunuyor | Depoyu **gizli yapmayın**. Gizli gerekirse görseller başka bir herkese açık yere taşınmalı. |
| 9 | **Görsel biçimi** | "görsel .jpg olmalı" | Instagram PNG kabul etmez | Üreticiler JPG yazar; yayıncı yüklemeden önce denetler. |
| 10 | **Türkçe büyük harf** | "TAHIN" | CSS büyük harfi dil verilmeden yapılınca i → I | Bütün üreticilerde `<html lang="tr">`. Kural voice.md'de. |
| 11 | **60 gün hareketsizlik** | zamanlanmış işler durur | GitHub, 60 gün commit olmayan herkese açık depoda zamanlamayı kapatır | Yayın durumu her gün commit edildiği için olmaz; uzun ara verilirse Actions sayfasından iş akışı yeniden etkinleştirilir. |
| 12 | **Günlük sınır** | "limit" hatası | API ile günde en fazla 100 paylaşım | Bizim kullanımımız günde 3-5; sorun olmaz. |

## Kullanıcının yapması gerekenler

- GitHub'dan "Run failed" e-postası gelirse Claude'a iletin (ekran görüntüsü yeter).
- Öne çıkan hikâyeye ekleme ve başkalarının gönderilerine yorum Instagram
  tarafından otomatiğe kapalı; bunlar elle yapılır.
- Meta uygulamasında ve GitHub ayarlarında bir şeyi değiştirmeden önce Claude'a sorun.
