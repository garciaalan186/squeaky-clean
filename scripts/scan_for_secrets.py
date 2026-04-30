#!/usr/bin/env python3
"""Standalone secret scanner.

Usage:
    python scripts/scan_for_secrets.py <path>

Recursively scans ``path`` for high-entropy API-key patterns and
blocked filenames (``.env``, ``*.pem``, ``id_rsa``, ...). Returns
exit code 1 on any hit, 0 on clean. Skips files >100 KB or with
binary suffixes (``.png``, ``.so``, ``.bin``, ...).

Bypass:
    SECRET_SCAN_BYPASS=1 forces a clean exit (use only in emergencies).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # so ``src.*`` imports resolve

from squeaky_clean.application.use_cases.secret_path_scanner import (  # noqa: E402
    SecretPathScanner,
)


def main(argv: list[str]) -> int:
    """Entry point: scan argv[1] (or '.') and report hits to stdout."""
    if os.environ.get("SECRET_SCAN_BYPASS") == "1":
        print("[secret-scan] BYPASSED via SECRET_SCAN_BYPASS=1", file=sys.stderr)
        return 0
    target = Path(argv[1]) if len(argv) > 1 else Path(".")
    if not target.exists():
        print(f"[secret-scan] path not found: {target}", file=sys.stderr)
        return 2
    hits = SecretPathScanner().scan(target)
    if not hits:
        print(f"[secret-scan] OK: no secrets in {target}")
        return 0
    print(f"[secret-scan] FAIL: {len(hits)} hit(s) in {target}", file=sys.stderr)
    for hit in hits:
        loc = f"{hit.path}:{hit.line}" if hit.line else str(hit.path)
        print(f"  {loc}  [{hit.label}]", file=sys.stderr)
    print(
        "[secret-scan] Set SECRET_SCAN_BYPASS=1 to override (emergency only).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
