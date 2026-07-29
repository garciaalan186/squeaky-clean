"""Self-conformance ratchet: the framework must obey the rules it enforces (R2.2).

Prime Directive — Clean Agent's own source passes every constraint it imposes
on generated projects. A hard zero-violation gate would block all work today
(171 pre-existing violations), so this is a RATCHET: it fails only on a NEW
violation. Removing violations is always allowed; run
``tests/self_conformance/regenerate_baseline.py`` to lock the improvement in.
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.self_conformance.conformance_scan import scan_violation_keys

_BASELINE = Path(__file__).with_name("baseline.json")


def _baseline() -> set[str]:
    return set(json.loads(_BASELINE.read_text()))


def test_no_new_self_conformance_violations() -> None:
    baseline = _baseline()
    current = scan_violation_keys()
    new = sorted(current - baseline)
    assert not new, (
        f"{len(new)} NEW self-conformance violation(s) — fix the code, do not "
        "add them to the baseline:\n" + "\n".join(f"  + {k}" for k in new)
    )


def test_baseline_is_not_stale_beyond_reason() -> None:
    """Warn-as-failure only if the baseline lists violations that no longer
    exist AND the drift is large — keeps the committed floor honest without
    failing on every incidental fix (regenerate to clear)."""
    baseline = _baseline()
    current = scan_violation_keys()
    removed = baseline - current
    # A little drift is fine (fixes land continuously); a large gap means the
    # baseline was never regenerated after a big cleanup — tighten it.
    assert len(removed) <= 25, (
        f"{len(removed)} baseline violations are already fixed — run "
        "tests/self_conformance/regenerate_baseline.py to tighten the floor."
    )
