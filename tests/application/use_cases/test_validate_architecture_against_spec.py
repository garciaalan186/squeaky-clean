"""Tests for ValidateArchitectureAgainstSpec."""

from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.entity_lifecycle import EntityLifecycle, StateTransition
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.query_semantic import QuerySemantic
from squeaky_clean.application.use_cases.validate_architecture_against_spec import (
    ValidateArchitectureAgainstSpec,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _spec(**kw: object) -> ProblemSpec:
    base: dict[str, object] = dict(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=["x"], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )
    base.update(kw)
    return ProblemSpec(**base)  # type: ignore[arg-type]


def _arch(*, classes: tuple[ClassSpec, ...] = (),
          invariants: tuple[str, ...] = ()) -> ArchitectureSpec:
    if not classes:
        classes = (ClassSpec(name="X", pattern="SimpleClass", implements=None,
                             methods=(), depends=(), concretes=()),)
    m = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(), depends=(),
                   classes=classes, invariants=invariants)
    return ArchitectureSpec(modules=(m,), graph=ArchitectureGraph(edges={}))


def test_missing_invariant_violation() -> None:
    p = _spec(domain_conventions=("timeline_includes_self",))
    a = _arch()
    v = ValidateArchitectureAgainstSpec().execute(a, p)
    assert any("timeline_includes_self" in x for x in v)


def test_present_invariant_clean() -> None:
    p = _spec(domain_conventions=("timeline_includes_self",))
    a = _arch(invariants=(
        "a user's timeline must include the user's own posts",))
    assert ValidateArchitectureAgainstSpec().execute(a, p) == ()


def test_missing_use_case_violation() -> None:
    p = _spec(query_semantics=(QuerySemantic(
        use_case="GetTimelineUseCase", shape="self_plus_followees"),))
    v = ValidateArchitectureAgainstSpec().execute(_arch(), p)
    assert any("GetTimelineUseCase" in x for x in v)


def test_missing_entity_violation() -> None:
    p = _spec(entity_lifecycle=(EntityLifecycle(entity="Tweet", transitions=(
        StateTransition(from_state="a", to_state="b", trigger="t"),)),))
    v = ValidateArchitectureAgainstSpec().execute(_arch(), p)
    assert any("Tweet" in x for x in v)


def test_missing_field_ref_violation() -> None:
    p = _spec(data_classification=(DataClassification(
        field_ref="User.password_hash", sensitivity="credential"),))
    v = ValidateArchitectureAgainstSpec().execute(_arch(), p)
    assert any("password_hash" in x for x in v)


def test_field_ref_present_clean() -> None:
    p = _spec(data_classification=(DataClassification(
        field_ref="User.password_hash", sensitivity="credential"),))
    cls = ClassSpec(name="User", pattern="Entity", implements=None, methods=(),
                    depends=(), concretes=(), fields=("password_hash: str",))
    assert ValidateArchitectureAgainstSpec().execute(
        _arch(classes=(cls,)), p) == ()
