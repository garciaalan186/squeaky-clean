"""StructuralHints: the part of a ProblemSpec that the Squib IR makes redundant.

Required patterns, bounded contexts, and node counts are all recoverable from
a Squib (see derive_structural_hints_from_squib). On the greenfield path they
act as hints to the RequirementCompiler; on the squib-first / recovery paths
they are derived from the IR rather than authored.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StructuralHints:
    """Structural expectations derivable from a Squib architecture."""

    required_bounded_contexts: list[str]
    required_patterns: list[str]
    expected_module_count: tuple[int, int]
    expected_class_count: tuple[int, int]
