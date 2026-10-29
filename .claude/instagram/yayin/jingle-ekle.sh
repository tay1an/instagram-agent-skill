#!/usr/bin/env bash
# Videoya Aziz Tahin jingle'ını ses kanalı olarak ekler (görüntü yeniden
# kodlanmaz). Kullanım:
#   jingle-ekle.sh GIRDI.mp4 CIKTI.mp4 [1|2] [BASLANGIC_SN]
# Jingle numarası verilmezse takvimdeki son kullanılanın tersi seçilir
# (sırayla 1, 2, 1, 2...). Başlangıç verilmezse muzik/jingle-N.txt'deki
# önerilen başlangıç kullanılır. Sonda 1,5 sn yumuşak kısılma.
set -euo pipefail
GIR=$1; CIK=$2; N=${3:-}; BAS=${4:-}
KOK=$(cd "$(dirname "$0")/.." && pwd)
if [ -z "$N" ]; then
  SON=$(python3 -c "
import json
d=json.load(open('$KOK/yayin/takvim.json'))
j=[p.get('jingle') for p in d['paylasimlar'] if p.get('jingle')]
print(j[-1] if j else 2)")
  N=$([ "$SON" = "1" ] && echo 2 || echo 1)
fi
[ -z "$BAS" ] && BAS=$(head -1 "$KOK/medya/muzik/jingle-$N.txt" 2>/dev/null || echo 0)
SURE=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$GIR")
KIS=$(python3 -c "print(max(0,$SURE-1.5))")
ffmpeg -loglevel error -y -i "$GIR" -ss "$BAS" -i "$KOK/medya/muzik/jingle-$N.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k \
  -af "afade=t=in:d=0.3,afade=t=out:st=$KIS:d=1.5,loudnorm=I=-14:TP=-1.5" \
  -t "$SURE" -movflags +faststart "$CIK"
echo "jingle-$N, $BAS sn'den, $SURE sn -> $CIK"
