"""TestObligation DTO: one deterministic test duty projected from the spec."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind


@dataclass(frozen=True)
class TestObligation:
    """A single duty a generated test must discharge to be faithful.

    Projected deterministically from the Squib + acceptance criteria, so
    verification is a pure function of the spec rather than a fuzzy
    comparison against the (possibly-gamed) test. ``target_class`` and
    ``method`` are the Squib-resolved subject; ``kind`` is the required
    assertion; ``detail`` carries the expected value / field / error hint;
    ``source`` is the originating criterion or invariant text.
    """

    target_class: str
    method: str
    kind: AssertionKind
    detail: str
    source: str
