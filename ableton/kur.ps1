# ableton-mcp-extended kurulumu (Windows). Ableton'un kurulu oldugu bilgisayarda PowerShell'de:
#   powershell -ExecutionPolicy Bypass -File ableton\kur.ps1
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/uisato/ableton-mcp-extended.git"
$Pin     = "11164498a31e782ca3d3f4ac67cbb526df0166e7"   # test edilen surum (2026-05-06)
$Hedef   = if ($env:ABLETON_MCP_DIR) { $env:ABLETON_MCP_DIR } else { Join-Path $env:USERPROFILE "ableton-mcp-extended" }
$Burasi  = $PSScriptRoot

$Py = (Get-Command py -ErrorAction SilentlyContinue)
$PyArgs = @()
if ($Py) { $PyArgs = @("-3") } else { $Py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Py) { throw "Python 3.10+ gerekli: https://www.python.org/downloads/ (Add to PATH isaretli)" }
& $Py.Source @PyArgs -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Python 3.10+ gerekli" }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git gerekli: https://git-scm.com" }

Write-Host "==> 1/5 Kod indiriliyor: $Hedef"
if (Test-Path (Join-Path $Hedef ".git")) { git -C $Hedef fetch -q origin } else { git clone -q $RepoUrl $Hedef }
git -C $Hedef -c advice.detachedHead=false checkout -q $Pin

Write-Host "==> 2/5 Sanal ortam + bagimliliklar"
& $Py.Source @PyArgs -m venv (Join-Path $Hedef ".venv")
$VPy = Join-Path $Hedef ".venv\Scripts\python.exe"
& $VPy -m pip install -q --upgrade pip
# Upstream 'pip install -e .' bozuk; server.py mcp 2.x ile acilmiyor -> mcp<2
& $VPy -m pip install -q "mcp[cli]>=1.3.0,<2" "python-dotenv>=1.0.0"
if ($LASTEXITCODE -ne 0) { throw "pip kurulumu basarisiz" }
& $VPy -m pip install -q -r (Join-Path $Burasi "requirements-analiz.txt")
if ($LASTEXITCODE -ne 0) { Write-Warning "Stem analiz paketleri kurulamadi; MCP yine de calisir." }

Write-Host "==> 3/5 Ableton Remote Script"
$Docs = [Environment]::GetFolderPath("MyDocuments")
$RS = Join-Path $Docs "Ableton\User Library\Remote Scripts"
New-Item -ItemType Directory -Force -Path (Join-Path $RS "AbletonMCP"), (Join-Path $RS "AbletonMCP_UDP") | Out-Null
Copy-Item (Join-Path $Hedef "AbletonMCP_Remote_Script\__init__.py") (Join-Path $RS "AbletonMCP\__init__.py") -Force
Copy-Item (Join-Path $Hedef "Ableton-MCP_hybrid-server\AbletonMCP_UDP\__init__.py") (Join-Path $RS "AbletonMCP_UDP\__init__.py") -Force
Write-Host "   -> $RS\AbletonMCP"

Write-Host "==> 4/5 MCP istemcileri"
$Server = Join-Path $Hedef "MCP_Server\server.py"
$Cfg = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
# Microsoft Store surumu farkli klasor kullanir
$Store = Get-ChildItem (Join-Path $env:LOCALAPPDATA "Packages") -Directory -Filter "Claude_*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($Store) { $Cfg = Join-Path $Store.FullName "LocalCache\Roaming\Claude\claude_desktop_config.json" }
& $VPy (Join-Path $Burasi "claude_config.py") $Cfg $VPy $Server
if (Get-Command claude -ErrorAction SilentlyContinue) {
  claude mcp remove -s user AbletonMCP 2>$null | Out-Null
  claude mcp add -s user AbletonMCP -- $VPy $Server
  Write-Host "   -> Claude Code (user scope)"
}

Write-Host "==> 5/5 Songwriter skill (Claude Code)"
$Skills = Join-Path $env:USERPROFILE ".claude\skills"
New-Item -ItemType Directory -Force -Path $Skills | Out-Null
Remove-Item (Join-Path $Skills "ableton-songwriter") -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $Hedef "skills\ableton-songwriter") $Skills -Recurse -Force

Write-Host @"

Kurulum tamam. Son adimlar (elle):
  1. Ableton Live'i ac/yeniden baslat -> Preferences -> Link, Tempo & MIDI
  2. Bos bir Control Surface yuvasinda 'AbletonMCP' sec, Input/Output = None
     Durum cubugunda: "AbletonMCP: Listening for commands on port 9877"
  3. Claude Desktop'i tamamen kapatip ac.
Stem analizi:  & "$VPy" "$Burasi\stem_analiz.py" <stem-klasoru>
"@
