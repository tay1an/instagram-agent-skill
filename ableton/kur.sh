#!/usr/bin/env bash
# ableton-mcp-extended kurulumu (macOS / Linux). Ableton'un kurulu oldugu bilgisayarda calistir.
#   bash ableton/kur.sh
set -euo pipefail

REPO_URL="https://github.com/uisato/ableton-mcp-extended.git"
PIN="11164498a31e782ca3d3f4ac67cbb526df0166e7"   # test edilen surum (2026-05-06)
HEDEF="${ABLETON_MCP_DIR:-$HOME/ableton-mcp-extended}"
BURASI="$(cd "$(dirname "$0")" && pwd)"

PY="$(command -v python3 || command -v python || true)"
[ -n "$PY" ] || { echo "Python 3.10+ gerekli: https://www.python.org/downloads/"; exit 1; }
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
  || { echo "Python 3.10+ gerekli (bulunan: $("$PY" --version))"; exit 1; }
command -v git >/dev/null || { echo "git gerekli"; exit 1; }

echo "==> 1/5 Kod indiriliyor: $HEDEF"
if [ -d "$HEDEF/.git" ]; then git -C "$HEDEF" fetch -q origin; else git clone -q "$REPO_URL" "$HEDEF"; fi
git -C "$HEDEF" -c advice.detachedHead=false checkout -q "$PIN"

echo "==> 2/5 Sanal ortam + bagimliliklar"
"$PY" -m venv "$HEDEF/.venv"
VPY="$HEDEF/.venv/bin/python"
"$VPY" -m pip install -q --upgrade pip
# Upstream'in 'pip install -e .' komutu bozuk (pyproject var olmayan paketi listeliyor),
# server.py de mcp 2.x ile acilmiyor. Bu yuzden bagimliliklari dogrudan, mcp<2 ile kuruyoruz.
"$VPY" -m pip install -q "mcp[cli]>=1.3.0,<2" "python-dotenv>=1.0.0"
"$VPY" -m pip install -q -r "$BURASI/requirements-analiz.txt" \
  || echo "   (uyari) stem analiz paketleri kurulamadi; MCP yine de calisir."

echo "==> 3/5 Ableton Remote Script"
case "$(uname -s)" in
  Darwin) RS="$HOME/Music/Ableton/User Library/Remote Scripts" ;;
  *)      RS="${ABLETON_REMOTE_SCRIPTS:-$HOME/Ableton/User Library/Remote Scripts}" ;;
esac
mkdir -p "$RS/AbletonMCP" "$RS/AbletonMCP_UDP"
cp "$HEDEF/AbletonMCP_Remote_Script/__init__.py" "$RS/AbletonMCP/__init__.py"
cp "$HEDEF/Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py" "$RS/AbletonMCP_UDP/__init__.py"
echo "   -> $RS/AbletonMCP"

echo "==> 4/5 MCP istemcileri"
SERVER="$HEDEF/MCP_Server/server.py"
if [ "$(uname -s)" = "Darwin" ]; then
  CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
  CFG="${XDG_CONFIG_HOME:-$HOME/.config}/Claude/claude_desktop_config.json"
fi
"$VPY" "$BURASI/claude_config.py" "$CFG" "$VPY" "$SERVER"
if command -v claude >/dev/null; then
  claude mcp remove -s user AbletonMCP >/dev/null 2>&1 || true
  claude mcp add -s user AbletonMCP -- "$VPY" "$SERVER" && echo "   -> Claude Code (user scope)"
fi

echo "==> 5/5 Songwriter skill (Claude Code)"
mkdir -p "$HOME/.claude/skills"
rm -rf "$HOME/.claude/skills/ableton-songwriter"
cp -R "$HEDEF/skills/ableton-songwriter" "$HOME/.claude/skills/ableton-songwriter"

cat <<MSG

Kurulum tamam. Son adimlar (elle):
  1. Ableton Live'i ac/yeniden baslat -> Preferences -> Link, Tempo & MIDI
  2. Bos bir Control Surface yuvasinda 'AbletonMCP' sec, Input/Output = None
     Durum cubugunda: "AbletonMCP: Listening for commands on port 9877"
  3. Claude Desktop'i tamamen kapatip ac.
Stem analizi:  "$VPY" "$BURASI/stem_analiz.py" <stem-klasoru>
MSG
