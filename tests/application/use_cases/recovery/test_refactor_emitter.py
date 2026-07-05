"""End-to-end test for RefactorEmitter (Squib + plan -> refactored Squib)."""

from pathlib import Path

from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.recovery.refactor_emitter import RefactorEmitter
from squeaky_clean.application.use_cases.recovery.refactor_plan_deserializer import (
    RefactorPlanDeserializer,
)
from squeaky_clean.application.use_cases.recovery.squib_emitter import SquibEmitter
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_SPEC = ArchitectureSpec(
    modules=(ModuleSpec(
        name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
        classes=(ClassSpec(
            name="Page", pattern="SimpleClass", implements=None,
            methods=("render(): str",), depends=(), concretes=(), fields=(),
            invariants=(),
        ),),
        invariants=(),
    ),),
    graph=ArchitectureGraph(edges={"Shop": ()}),
)


def _run(tmp: Path) -> object:
    squib = tmp / "recovered.squib"
    squib.write_text(SquibEmitter().emit(_SPEC))
    plan = tmp / "refactor_plan.json"
    plan.write_text('{"fix": ["framework-coupling:app.page.Page"], "ignore": []}')
    return RefactorEmitter().emit(squib, plan, tmp / "refactored.squib")


def test_emits_refactored_squib_with_the_split(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    spec = ParseArchitectureNotation().parse(
        Path(summary.out_path).read_text(),  # type: ignore[attr-defined]
    )
    names = {c.name for m in spec.modules for c in m.classes}
    assert {"Page", "PageRepository", "PageAdapter"} <= names
    assert spec.validate() == ()


def test_summary_reports_one_to_n_growth(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    assert summary.classes_before == 1  # type: ignore[attr-defined]
    assert summary.classes_after == 3  # type: ignore[attr-defined]  # Entity+Repo+Adapter


def test_plan_deserializer_round_trips() -> None:
    plan = RefactorPlanDeserializer().deserialize('{"fix": ["a"], "ignore": ["b"]}')
    assert plan.fix == ("a",)
    assert plan.ignore == ("b",)
