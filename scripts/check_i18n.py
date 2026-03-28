#!/usr/bin/env python3
"""i18n completeness checker.

Reads frontend/messages/de.json and frontend/messages/en.json,
computes the symmetric key difference (all nested key paths),
and exits non-zero when any keys are missing in either file.

Usage:
    python3 scripts/check_i18n.py

Can also be run via `make lint-i18n`.
"""

import json
import sys
from pathlib import Path


def flatten_keys(obj: dict, prefix: str = "") -> set[str]:
    """Return a set of dot-delimited leaf key paths from a nested dict."""
    keys: set[str] = set()
    for k, v in obj.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= flatten_keys(v, full)
        else:
            keys.add(full)
    return keys


def main() -> int:
    root = Path(__file__).resolve().parent.parent / "frontend" / "messages"
    de_path = root / "de.json"
    en_path = root / "en.json"

    if not de_path.exists():
        print(f"ERROR: {de_path} not found", file=sys.stderr)
        return 1
    if not en_path.exists():
        print(f"ERROR: {en_path} not found", file=sys.stderr)
        return 1

    de_keys = flatten_keys(json.loads(de_path.read_text(encoding="utf-8")))
    en_keys = flatten_keys(json.loads(en_path.read_text(encoding="utf-8")))

    missing_in_en = sorted(de_keys - en_keys)
    missing_in_de = sorted(en_keys - de_keys)

    ok = True

    if missing_in_en:
        print(f"MISSING IN en.json ({len(missing_in_en)} key(s)):")
        for k in missing_in_en:
            print(f"  - {k}")
        ok = False

    if missing_in_de:
        print(f"MISSING IN de.json ({len(missing_in_de)} key(s)):")
        for k in missing_in_de:
            print(f"  - {k}")
        ok = False

    if ok:
        print(f"OK: {len(de_keys)} keys match in both de.json and en.json")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
