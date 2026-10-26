#!/usr/bin/env python3
"""Zifir hesabının haftalık raporu: instagram_rapor.py'yi Zifir'in klasörüne yazdırır."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import instagram_rapor  # noqa: E402

instagram_rapor.KLASOR = ".claude/zifir/rapor"

if __name__ == "__main__":
    try:
        sys.exit(instagram_rapor.main())
    except instagram_rapor.ApiHatasi as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)
