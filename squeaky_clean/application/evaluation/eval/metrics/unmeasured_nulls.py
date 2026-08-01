"""unmeasured_nulls: JSON payloads must not render unmeasured metrics as 0.0."""

from __future__ import annotations

_SCHEMA_VERSION = 2  # R6.3: nested VO payloads (test_outcome, cost, ...)


def null_unmeasured(payload: dict[str, object]) -> dict[str, object]:
    """Null unmeasured values in an EvalMetrics payload; stamp schema_version.

    A security score of 0.0 with ``security_test_count == 0`` means "not
    measured" (``--security-tests`` off), not "everything failed" — every
    recent dashboard rendered the two identically (R5.3). ``None``
    serialises to JSON ``null``, which readers can distinguish. Since
    schema v2 the affected fields live in the nested ``test_outcome``
    value-object payload.
    """
    payload["schema_version"] = _SCHEMA_VERSION
    outcome = payload.get("test_outcome")
    if not isinstance(outcome, dict):
        return payload
    if outcome.get("security_test_count") == 0:
        outcome["security_tests_pass"] = None
    if outcome.get("tests_collected") == 0 and (
        outcome.get("test_status") == "not_measured"
    ):
        outcome["tests_pass"] = None
        outcome["functional_tests_pass"] = None
    return payload
