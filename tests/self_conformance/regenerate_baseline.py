"""Regenerate the self-conformance baseline (R2.2).

Run after LEGITIMATELY reducing violations (splitting an over-long file, fixing
a layer import) so the ratchet locks in the improvement:

    python tests/self_conformance/regenerate_baseline.py

The ratchet only ever fails on NEW violations, so a stale (too-large) baseline
never blocks work — regenerating simply tightens the floor. Adding violations
here to silence the test is the wrong move; fix the code instead.
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.self_conformance.conformance_scan import scan_violation_keys

_BASELINE = Path(__file__).with_name("baseline.json")


def main() -> None:
    keys = sorted(scan_violation_keys())
    _BASELINE.write_text(json.dumps(keys, indent=2) + "\n")
    print(f"wrote {_BASELINE} with {len(keys)} keys")


if __name__ == "__main__":
    main()
