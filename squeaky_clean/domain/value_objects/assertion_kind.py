"""AssertionKind: the deterministic shape of a test obligation's assertion."""

from enum import Enum


class AssertionKind(Enum):
    """What a test must assert to discharge an obligation.

    Derived deterministically from a criterion's Then clause (or a
    structured ``expected_outcomes`` entry). ``CALL_ONLY`` is the floor:
    the method must at least be invoked when the outcome is unstructured.
    """

    RAISES = "raises"
    EQUALS = "equals"
    FIELD_HOLDS = "field_holds"
    CALL_ONLY = "call_only"
