# Meta incelemesi: yorumlara otomatik tarif DM'i için gelişmiş erişim

Amaç: "AzizTahin" Meta uygulamasının, uygulamada rolü olmayan herkesin
yorumlarını okuyabilmesi ve onlara DM gönderebilmesi. Bunun için Meta'nın
"Advanced Access" (gelişmiş erişim) vermesi gerekir.

Süre: belgeler hazırsa işletme doğrulaması birkaç gün, inceleme 1-2 hafta.
Meta ilk başvuruyu reddedebilir; red gerekçesine göre düzeltip yeniden
başvurulur.

## Adımlar

| # | adım | kim | durum |
| --- | --- | --- | --- |
| 1 | Gizlilik ve veri silme sayfalarını yayınla (GitHub Pages) | siz | |
| 2 | Meta App settings → Basic: gizlilik URL, veri silme URL, simge, kategori, e-posta | siz | |
| 3 | İşletme portföyü oluştur ve uygulamaya bağla | siz | |
| 4 | İşletme doğrulaması (belge yükleme) | siz | |
| 5 | Demo için ikinci bir Instagram hesabını test kullanıcısı yap, otomasyonu aç | siz + Claude | |
| 6 | Ekran videosu kaydet (aşağıdaki senaryo) | siz | |
| 7 | İnceleme başvurusu: izin açıklamaları (aşağıda hazır) + video | siz | |

### 3. İşletme portföyü

1. https://business.facebook.com adresinde **Create a business portfolio**:
   işletme adı "Aziz Tahin", adınız, işletme e-postası.
2. **Business settings → Accounts → Apps → Add → Connect an app ID**:
   AzizTahin uygulamasının ID'si (Meta uygulama panelinde, sol üstte).

### 4. İşletme doğrulaması

**Business settings → Security Center → Start verification**. İstenen bilgiler
etiketinizdekilerle aynı olmalı:

- Yasal işletme adı (vergi levhasındaki ad)
- Adres: Alamescit Mh. İnönü Cad. No:51 Osmangazi/Bursa
- Telefon, web sitesi (aziztahin.com), e-posta (info@aziztahin.com)
- Belge: **vergi levhası** ya da **ticaret sicil gazetesi**; bazen işletme
  adına bir fatura (elektrik, internet) da kabul edilir.

### 5. Demo hazırlığı

- Meta uygulama panelinde **App roles → Roles → Instagram Testers**'a ikinci
  bir Instagram hesabı ekleyin (kişisel hesabınız ya da bir yakınınızın) ve
  daveti https://www.instagram.com/accounts/manage_access/ adresinden kabul
  edin.
- Claude, GitHub'da yorum otomasyonunu açar (depo değişkeni
  `YORUM_OTOMASYONU=acik`). Test kullanıcısının yorumları geliştirme modunda
  da görünür, bu yüzden demo çalışır.

### 6. Ekran videosu senaryosu (1-2 dakika, ekran kaydı)

1. Test hesabıyla @aziz.tahin'in bir gönderisine `TAHİN` yorumu yazılır.
2. Birkaç dakika sonra (ya da GitHub Actions'ta iş elle çalıştırılarak)
   yorumun altında "DM'den yazdık 🤎" cevabı ve test hesabının DM kutusunda
   Aziz Tahin'den gelen mesaj gösterilir.
3. Test hesabı mesaja "Evet" yazar; tarif mesajlarının geldiği gösterilir.
4. Videoda ses gerekmez; ekrana kısa İngilizce açıklama yazıları eklenebilir:
   "User comments TAHİN", "App sends a private reply", "User replies, app
   sends the recipe list".

### 7. Başvuru metinleri (İngilizce, kopyalayıp yapıştırın)

**Permissions and features** sayfasında aşağıdaki izinlerin yanındaki
**Request advanced access** düğmesine basın, sonra **App Review → Requests**
bölümünden başvuruyu doldurun.

**instagram_business_basic**

```
Our app is used only by our own business, Aziz Tahin (a family-run tahini producer in Bursa, Turkey), on our own Instagram professional account @aziz.tahin. We use instagram_business_basic to read our account's profile ID and our own media list, so the app knows which of our posts to check for comments.
```

**instagram_business_manage_comments**

```
On our posts we invite followers to comment the keyword "TAHİN" to receive our free list of 5 tahini recipes. We use instagram_business_manage_comments to read the comments on our own media, detect comments that consist only of this keyword, and post a short public reply ("We sent you a DM") under the comment. We do not store comment text or usernames; we keep only comment IDs for up to 30 days to avoid replying twice.
```

**instagram_business_manage_messages**

```
When a user comments "TAHİN" on our post, we use instagram_business_manage_messages to send exactly one private reply to that comment, asking whether they would like the recipes. Only if the user replies to us within 24 hours do we send the recipe list in a few text messages, followed by information on how to order. We never message users who did not comment the keyword or did not reply, and we keep only Instagram-scoped IDs for up to 30 days. Users can request deletion at https://tay1an.github.io/instagram-agent-skill/veri-silme.html.
```

**Test talimatları (Notes for reviewer)**

```
1. Comment "TAHİN" on any recent post of @aziz.tahin.
2. Within 15 minutes the app replies publicly under the comment and sends a private reply DM.
3. Reply anything to that DM; within 15 minutes the app sends the recipe list.
The app runs as a scheduled server job every 15 minutes, so replies are not instant. The screencast shows the full flow with a test user.
```
