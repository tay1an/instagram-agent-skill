# Hesaplar

Bu depo iki Instagram hesabını yönetir. `.claude/skills/` altındaki ig-*
skill'leri ikisi için de kullanılır.

| hesap | klasör | erişim anahtarı (GitHub secret) |
| --- | --- | --- |
| @aziz.tahin (tahin dükkânı) | `.claude/instagram/` | `IG_ACCESS_TOKEN` |
| @zifir.123 (Zifir, müzisyen, Türkçe duygusal pop) | `.claude/zifir/` | `IG_ACCESS_TOKEN_ZIFIR` |

Skill'ler `~/.claude/instagram/voice.md`, `plan.md`, `log.md`, `swipe.md`
dediğinde, o an hangi hesap için çalışılıyorsa o hesabın klasöründeki dosyayı
kullan. Hangi hesap olduğu belli değilse sor. Bir hesabın marka kurallarını ve
sesini öbürüne taşıma.

Her klasörde aynı yapı var: `voice.md`, `plan.md`, `log.md`, `rapor/`
(haftalık istatistikler, GitHub her cumartesi yazar) ve `yayin/takvim.json`
(otomatik yayın takvimi, kurulumu `yayin/KURULUM.md`). Zifir'in videoları
`.claude/zifir/medya/` altında.
