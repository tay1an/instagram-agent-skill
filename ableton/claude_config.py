"""Claude Desktop config'ine AbletonMCP sunucusunu ekler; mevcut sunuculara dokunmaz.

Kullanim: python claude_config.py <config.json> <python-yolu> <server.py-yolu>
"""
import json
import shutil
import sys
from pathlib import Path


def main(cfg_path: str, python: str, server: str) -> None:
    cfg = Path(cfg_path)
    data = {}
    if cfg.exists() and cfg.read_text(encoding="utf-8").strip():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            sys.exit(f"{cfg} gecerli JSON degil; elle duzeltip tekrar calistir.")
        shutil.copy2(cfg, cfg.with_suffix(".json.bak"))
    data.setdefault("mcpServers", {})["AbletonMCP"] = {"command": python, "args": [server]}
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"   -> Claude Desktop: {cfg}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
