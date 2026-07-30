"""unmeasured_nulls: JSON payloads must not render unmeasured metrics as 0.0."""

from __future__ import annotations


def null_unmeasured(payload: dict[str, object]) -> dict[str, object]:
    """Replace unmeasured metric values with None in an EvalMetrics payload.

    A security score of 0.0 with ``security_test_count == 0`` means "not
    measured" (``--security-tests`` off), not "everything failed" — every
    recent dashboard rendered the two identically (R5.3). ``None``
    serialises to JSON ``null``, which readers can distinguish.
    """
    if payload.get("security_test_count") == 0:
        payload["security_tests_pass"] = None
    if payload.get("tests_collected") == 0 and (
        payload.get("test_status") == "not_measured"
    ):
        payload["tests_pass"] = None
        payload["functional_tests_pass"] = None
    return payload
