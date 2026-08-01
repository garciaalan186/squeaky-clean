"""Tests for ClassLineRenderer (extracted from the context formatter)."""

from squeaky_clean.application.generation.testgen.prompting.class_line_renderer import (
    ClassLineRenderer,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
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


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=1, slug="x", description="d",
        required_bounded_contexts=["m"],
        acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["Entity"],
        target_language=TargetLanguage.PYTHON,
    )


def _cls(name: str) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="Entity", implements=None,
        methods=("validate(): Result",), depends=(), concretes=(),
        fields=("id: str",),
    )


def _module(name: str, cls: ClassSpec) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=LayerType.DOMAIN, exports=(cls.name,),
        depends=(), classes=(cls,), invariants=(),
    )


def test_unlayered_line_has_no_file_path() -> None:
    module = _module("Billing", _cls("Payment"))
    ctx = TestArchitectureContext(module=module, problem=_problem())
    line = ClassLineRenderer(ctx).class_line(module.classes[0], module)
    assert line == ("  - Payment [Entity] fields=[id: str] "
                    "methods=[validate(): Result]")


def test_layered_line_appends_dotted_file_path() -> None:
    module = _module("Billing", _cls("Payment"))
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    ctx = TestArchitectureContext(
        module=module, problem=_problem(), toolkit=toolkit,
    )
    line = ClassLineRenderer(ctx).class_line(module.classes[0], module)
    assert line.endswith("file=src.domain.billing.payment")


def test_cross_module_lists_only_exported_sibling_classes() -> None:
    focal = _module("Billing", _cls("Payment"))
    sibling = _module("Ledger", _cls("LedgerEntry"))
    hidden = ModuleSpec(
        name="Secrets", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(_cls("Hidden"),), invariants=(),
    )
    arch = ArchitectureSpec(
        modules=(focal, sibling, hidden),
        graph=ArchitectureGraph(edges={}),
    )
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    ctx = TestArchitectureContext(
        module=focal, problem=_problem(), toolkit=toolkit, architecture=arch,
    )
    lines = ClassLineRenderer(ctx).cross_module(focal, arch)
    assert len(lines) == 1
    assert "LedgerEntry" in lines[0] and "Hidden" not in lines[0]
