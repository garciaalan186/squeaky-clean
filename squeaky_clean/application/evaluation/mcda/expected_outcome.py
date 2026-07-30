"""ExpectedOutcome DTO: structured criterion outcome (the `expect:` schema).

The §Notation extension that makes obligation VALUES deterministic. When a
criterion's Then clause is free text, an ``expected_outcomes`` entry keyed
by the criterion's verb pins the assertion kind and value, so the projector
does not have to interpret prose.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedOutcome:
    """A structured outcome for the criterion whose When-verb is ``verb``.

    ``kind`` is one of the AssertionKind values ("raises" / "equals" /
    "field_holds" / "call_only"); ``value`` is the expected value (EQUALS),
    field name (FIELD_HOLDS), or error hint (RAISES).
    """

    verb: str
    kind: str
    value: str = ""
