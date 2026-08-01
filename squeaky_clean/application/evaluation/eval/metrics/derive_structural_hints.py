"""derive_structural_hints_from_squib: project a Squib IR to StructuralHints.

Makes the ProblemSpec/Squib redundancy explicit: the structural half of a
ProblemSpec is a deterministic function of the architecture. This is the
generalized core of the recovery path's ProblemSpecSynthesizer.
"""

from squeaky_clean.application.shared.problem.structural_hints import StructuralHints
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def derive_structural_hints_from_squib(
    architecture: ArchitectureSpec,
) -> StructuralHints:
    """Derive the structural expectations a Squib already encodes."""
    modules = architecture.modules
    classes = [c for m in modules for c in m.classes]
    patterns: list[PatternName] = sorted({c.pattern for c in classes})
    contexts = [m.name for m in modules]
    return StructuralHints(
        required_bounded_contexts=contexts,
        required_patterns=patterns,
        expected_module_count=(len(modules), len(modules)),
        expected_class_count=(len(classes), len(classes)),
    )
