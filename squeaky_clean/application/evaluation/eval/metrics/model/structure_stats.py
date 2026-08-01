"""StructureStats value object: generated-code shape + ACS scores (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StructureStats:
    """Immutable file-shape statistics and Architectural Complexity Score.

    ``acs_*`` fields follow BENCHMARK_METHODOLOGY.md; ``acs_normalized``
    defaults to 1.0 (P0 baseline). ``classes_per_module`` is a tuple so
    the value object stays deeply immutable (serialises as a JSON array,
    same as the former list).
    """

    avg_file_line_count: float = 0.0
    max_file_line_count: int = 0
    max_methods_per_class: int = 0
    max_args_per_method: int = 0
    classes_per_module: tuple[int, ...] = ()
    orphan_files: int = 0
    acs_structural: float = 0.0
    acs_codegen: float = 0.0
    acs_constraint: float = 0.0
    acs_composite: float = 0.0
    acs_normalized: float = 1.0
    acs_cost_per_unit: float = 0.0
    acs_velocity: float = 0.0
