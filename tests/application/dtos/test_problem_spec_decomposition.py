"""ProblemSpec decomposition: behavior oracle vs Squib-derivable structure."""

from squeaky_clean.application.evaluation.eval.metrics.derive_structural_hints import (
    derive_structural_hints_from_squib,
)
from squeaky_clean.application.evaluation.eval.metrics.structural_hints import StructuralHints
from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.shared.problem.behavior_spec import BehaviorSpec
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver

_SQUIB = """MODULE Cart
LAYER Domain
EXPORTS [Cart]
DEPENDS []
CLASSES {
  Cart -> Entity { methods: [total(): int] }
  Money -> ValueObject { fields: [amount: int] }
  Discount -> Strategy { methods: [apply(total: int): int] }
}
"""


def test_behavior_view_holds_the_acceptance_oracle() -> None:
    problem = ProblemResolver().resolve("P2")
    behavior = problem.behavior
    assert isinstance(behavior, BehaviorSpec)
    assert behavior.acceptance_criteria == problem.acceptance_criteria
    assert behavior.acceptance_criteria  # P2 has criteria


def test_structural_view_holds_the_derivable_half() -> None:
    problem = ProblemResolver().resolve("P2")
    hints = problem.structural_hints
    assert isinstance(hints, StructuralHints)
    assert hints.required_patterns == problem.required_patterns


def test_structural_hints_are_derivable_from_a_squib() -> None:
    arch = ParseArchitectureNotation().parse(_SQUIB)
    hints = derive_structural_hints_from_squib(arch)
    assert hints.required_patterns == ["Entity", "Strategy", "ValueObject"]
    assert hints.required_bounded_contexts == ["Cart"]
    assert hints.expected_module_count == (1, 1)
    assert hints.expected_class_count == (3, 3)
