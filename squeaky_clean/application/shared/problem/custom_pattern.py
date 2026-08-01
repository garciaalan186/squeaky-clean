"""CustomPattern: one externally-supplied pattern name + ICP spec stem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomPattern:
    """One externally-supplied pattern: name + ICP spec stem.

    ``name`` is deliberately `str`, not PatternName: a custom pattern's
    identity is precisely a name OUTSIDE the 34-member catalog Literal
    (e.g. EventSourcedAggregate).
    """

    name: str
    emitter_spec_name: str
