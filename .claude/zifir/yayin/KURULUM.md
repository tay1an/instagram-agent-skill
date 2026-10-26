# Zifir: otomatik Instagram yayını kurulumu

`.claude/zifir/yayin/takvim.json` dosyasındaki paylaşımlar zamanı gelince
@zifir.123 hesabında kendiliğinden yayınlanır. GitHub her 15 dakikada bir
kontrol eder (`Zifir yayın` iş akışı).

**Tahin hesabından tamamen ayrıdır:** Zifir'in kendi Meta uygulaması, kendi
GitHub anahtarları (`ZIFIR_IG_TOKEN`, `ZIFIR_GH_TOKEN`) ve kendi iş akışları
(`zifir-yayin.yml`, `zifir-rapor.yml`, `zifir-token-yenile.yml`) vardır.
Tahin'in uygulamasına, anahtarlarına ve iş akışlarına dokunulmaz.

> **Önemli:** Erişim anahtarlarını hiçbir zaman sohbete yapıştırmayın.
> Yalnızca GitHub'daki gizli alana yapıştırın.

---

## 1. Zifir için ayrı bir Meta uygulaması oluşturun

1. https://developers.facebook.com/apps → **Uygulama oluştur** (Create app).
2. Uygulama adı: `Zifir Yayin`.
3. Kullanım durumu: **"Instagram'da mesajları ve içeriği yönet"**
   (Manage messaging & content on Instagram).
4. İşletme portföyü sorulursa **"Şimdilik bağlama"** seçilebilir.

## 2. Zifir'i test kullanıcısı yapın

1. Yeni uygulamada **App roles → Roles → Instagram Testers → Add Instagram
   Testers** → `zifir.123`.
2. zifir.123 ile https://www.instagram.com/accounts/manage_access/ →
   **Tester Invites** → daveti kabul edin.

## 3. Erişim anahtarını alın

1. **Kullanım durumları → Customize → API setup with Instagram login →
   Generate access tokens → Add account** → zifir.123 ile giriş yapıp
   bütün izinleri verin.
2. **Generate token** → açılan pencerede "IG" ile başlayan uzun metni
   **Copy** ile kopyalayın (hesap numarasını değil).

## 4. GitHub'a kaydedin

https://github.com/tay1an/instagram-agent-skill/settings/secrets/actions →
**New repository secret**:

| Name | Secret |
| --- | --- |
| `ZIFIR_IG_TOKEN` | 3. adımda kopyalanan anahtar |
| `ZIFIR_GH_TOKEN` | aşağıdaki GitHub anahtarı |

`ZIFIR_GH_TOKEN` için: https://github.com/settings/personal-access-tokens/new
→ ad `zifir anahtar yenileme`, en uzun süre, **Only select repositories** →
`tay1an/instagram-agent-skill`, **Repository permissions → Secrets: Read and
write** → Generate token.

## 5. Deneyin

Claude, `Zifir yayın` iş akışını **Deneme** modunda bir kez çalıştırır. Kayıtta
`Bağlantı tamam: @zifir.123` görünmelidir. Ardından tek bir paylaşım denenir.
Art arda deneme yapılmaz; bir hata olursa önce nedeni bulunur.

---

## Bilmeniz gerekenler

- Takvimdeki paylaşımlar kurulum bitene kadar `taslak` durumundadır ve
  yayınlanmaz. Kurulum bitince Claude tarihleri ayarlayıp `bekliyor` yapar.
- 3 saatten fazla gecikmiş bir paylaşım yayınlanmaz ("atlandi" olur).
- API ile paylaşılan reel'lere Instagram müzik kütüphanesinden şarkı ve "AI
  ile oluşturuldu" etiketi eklenemez. Videolar şarkının kendi sesiyle çıkar.
- **TikTok bu sisteme dahil değil.** TikTok için tiktok.com/upload adresindeki
  "Zamanla" seçeneğini kullanın.
- Depo herkese açık olduğu için videolar ve açıklamalar yayın saatinden önce
  GitHub'da görülebilir.
