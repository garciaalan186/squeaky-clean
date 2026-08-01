"""Tests for ClassPathsBlockRenderer."""

from squeaky_clean.application.generation.emission.class_paths_block_renderer import (
    ClassPathsBlockRenderer,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _cls(name: str) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="Entity", implements=None,
        methods=(), depends=(), concretes=(),
    )


def _module(name: str, *classes: ClassSpec) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=classes, invariants=(),
    )


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="P0", tier=0, slug="calc", description="x",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def _toolkit() -> LanguageToolkit:
    return LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def test_no_toolkit_renders_nothing() -> None:
    ctx = TestArchitectureContext(module=_module("Payment", _cls("Payment")), problem=_problem())
    assert ClassPathsBlockRenderer().render(ctx) == []


def test_module_with_no_classes_renders_nothing() -> None:
    ctx = TestArchitectureContext(
        module=_module("Payment"), problem=_problem(), toolkit=_toolkit(),
    )
    assert ClassPathsBlockRenderer().render(ctx) == []


def test_single_module_renders_one_dotted_path_per_class() -> None:
    ctx = TestArchitectureContext(
        module=_module("Payment", _cls("Payment"), _cls("PaymentId")),
        problem=_problem(), toolkit=_toolkit(),
    )
    assert ClassPathsBlockRenderer().render(ctx) == [
        "  - Payment: src.domain.payment.payment",
        "  - PaymentId: src.domain.payment.payment_id",
    ]


def test_architecture_walks_siblings_and_dedupes_repeated_names() -> None:
    focal = _module("Payment", _cls("Payment"))
    sibling = _module("Billing", _cls("Payment"), _cls("Invoice"))
    arch = ArchitectureSpec(modules=(focal, sibling), graph=ArchitectureGraph(edges={}))
    ctx = TestArchitectureContext(
        module=focal, problem=_problem(), toolkit=_toolkit(), architecture=arch,
    )
    assert ClassPathsBlockRenderer().render(ctx) == [
        "  - Payment: src.domain.payment.payment",
        "  - Invoice: src.domain.billing.invoice",
    ]
