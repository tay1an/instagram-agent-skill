# Ableton ajanı: Suno stem'lerinden sıfırdan beste

Bu klasör [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended)
(MIT) projesini kurar ve eksik kalan bir parçayı tamamlar: **stem analizi**.

| Parça | Görev |
|---|---|
| `ableton-mcp-extended` (MCP sunucusu + Remote Script) | Claude'un Ableton'u yönetmesini sağlar: track, clip, nota, cihaz, arrangement, otomasyon (46 araç) |
| `stem_analiz.py` | Suno stem'lerini dinleyip tempo, ton, bölüm, akor, bas/vokal melodisi ve davul paternini çıkarır |
| `ableton-songwriter` skill'i | Upstream'deki besteleme iş akışı (brief, form, düzenleme, hızlı miks) |

> **Önemli:** MCP sunucusu Ableton'a `localhost:9877` üzerinden bağlanır. Bu yüzden kurulumu
> **Ableton'un çalıştığı bilgisayarda** yapman gerekiyor. Bulut oturumundan Ableton'a ulaşılamaz.

## Kurulum

Ön koşullar: Ableton Live 11+, Python 3.10+, git, Claude Desktop ve/veya Claude Code.

macOS / Linux:

```bash
git clone -b claude/focused-albattani-smt8hp https://github.com/tay1an/instagram-agent-skill.git
```

```bash
bash instagram-agent-skill/ableton/kur.sh
```

Windows (PowerShell):

```bash
powershell -ExecutionPolicy Bypass -File instagram-agent-skill\ableton\kur.ps1
```

Script şunları yapar:

1. `~/ableton-mcp-extended` klasörüne test edilmiş sürümü (`1116449`) indirir.
2. Ayrı bir `.venv` kurar, `mcp<2` ile bağımlılıkları yükler (aşağıdaki nota bak).
3. `AbletonMCP` ve `AbletonMCP_UDP` Remote Script'lerini User Library'ye kopyalar.
4. Claude Desktop config'ine `AbletonMCP` sunucusunu **ekler** (diğer sunuculara dokunmaz,
   eski dosyayı `.json.bak` olarak yedekler). `claude` komutu varsa Claude Code'a da ekler.
5. `ableton-songwriter` skill'ini `~/.claude/skills/` altına koyar.

Ardından elle yapılacaklar:

1. Ableton → **Preferences → Link, Tempo & MIDI** → boş bir Control Surface yuvasında
   **AbletonMCP** seç, Input/Output = **None**. Durum çubuğunda
   `AbletonMCP: Listening for commands on port 9877` görünmeli.
2. Claude Desktop'ı tamamen kapatıp yeniden aç.
3. Test: *"Ableton oturumum hakkında bilgi ver"*.

### Upstream'e göre düzeltmeler

- Upstream'deki `pip install -e .` çalışmıyor: `pyproject.toml` var olmayan bir
  `AbletonMCP_UDP` paketini listeliyor. Script bu adımı atlayıp bağımlılıkları doğrudan kuruyor.
- `server.py`, `mcp` 2.x ile açılmıyor (`FastMCP` adı değişti). `mcp<2` sabitlendi;
  1.30.0 ile 46 aracın listelendiği doğrulandı.
- Config'te `python` yerine venv'in tam yolu kullanılıyor. Böylece "Python not found" hatası çıkmaz.

## İş akışı: Suno → Ableton

1. Suno'dan stem'leri indir (Vocals, Bass, Drums, Instrumental/Other...), bir klasöre koy.
2. Analiz et:

   ```bash
   ~/ableton-mcp-extended/.venv/bin/python instagram-agent-skill/ableton/stem_analiz.py ~/Music/suno/sarkim
   ```

   Suno tempoyu söylüyorsa `--bpm 124` ver, tahminden daha güvenilirdir.
   Çıktılar: `analiz.json` (tam veri) ve `analiz.md` (özet).
3. Claude'a ver:

   > `~/Music/suno/sarkim/analiz.json` dosyasını oku. /ableton-songwriter akışıyla bu şarkıyı
   > Ableton'da sıfırdan kur: tempoyu ayarla, her stem için MIDI track aç, uygun enstrümanı
   > yükle, notaları `add_notes_to_clip` ile yaz, bölümlere cue point koy ve arrangement'a
   > diz. Orijinal stem'leri de referans olarak ayrı audio track'lere koy ve sessize al.

Stem dosya adından rol tahmin edilir: `vocal/vox` → vokal, `bass/808` → bas,
`drum/kick/snare/hat/perc` → davul, `lead/melody` → melodi, geri kalanlar → akor.

## Sınırlar

- Transkripsiyon yaklaşıktır. Bas ve vokal melodisi (pyin) genelde iyidir. Akorlar majör/minör
  üçlü olarak tahmin edilir. Davul sadece kick/snare/hat diye üçe ayrılır. Sonucu kulakla kontrol et.
- Sabit tempo ve 4/4 varsayılır (Suno çıktıları için genelde doğru).
- Sentetik testte (120 BPM, A minör, Am–F–C–G, 16 bar) tempo, ton, akorlar, bas, vokal melodisi ve davul birebir doğru çıktı; gerçek Suno miksleri bu kadar temiz değildir.
- Analiz, şarkı başına bir-iki dakika sürebilir. En yavaş adım vokal ve bas perde takibi.
