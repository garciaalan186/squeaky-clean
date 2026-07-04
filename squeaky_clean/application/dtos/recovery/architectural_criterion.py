"""ArchitecturalCriterion: the shared architectural trade-off criteria."""

from typing import Literal, get_args

ArchitecturalCriterion = Literal[
    "testability",
    "simplicity",
    "performance",
    "evolvability",
    "migration_safety",
    "delivery_speed",
]

ALL_ARCHITECTURAL_CRITERIA: tuple[str, ...] = tuple(get_args(ArchitecturalCriterion))
