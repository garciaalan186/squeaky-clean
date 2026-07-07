"""Tests for ProjectTestObligations — deterministic spec -> obligations."""

from squeaky_clean.application.dtos.expected_outcome import ExpectedOutcome
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _arch() -> ArchitectureSpec:
    ingest = ClassSpec(
        name="Ingester", pattern="UseCase", implements=None,
        methods=("ingest_event(body: str): Event",), depends=(), concretes=())
    body = ClassSpec(
        name="RawBody", pattern="ValueObject", implements=None, methods=(),
        depends=(), concretes=(), fields=("value: str",),
        invariants=("value must not be empty",))
    mod = ModuleSpec(name="M", layer=LayerType.APPLICATION, exports=(),
                     depends=(), classes=(ingest, body), invariants=())
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def _problem(criteria: list[str],
             outcomes: tuple[ExpectedOutcome, ...] = ()) -> ProblemSpec:
    return ProblemSpec(
        id="P", tier=0, slug="p", description="", required_bounded_contexts=[],
        acceptance_criteria=criteria, expected_module_count=(1, 1),
        expected_class_count=(1, 2), required_patterns=[],
        target_language=TargetLanguage.PYTHON, expected_outcomes=outcomes)


def test_criterion_resolves_verb_to_class_and_raises_kind() -> None:
    obs = ProjectTestObligations().project(
        _arch(),
        _problem(["Given empty, When ingest_event is called, Then an error is raised"]))
    crit = [o for o in obs if o.source.startswith("Given")]
    assert len(crit) == 1
    assert crit[0].target_class == "Ingester"
    assert crit[0].method == "ingest_event"
    assert crit[0].kind is AssertionKind.RAISES


def test_equals_then_grammar_extracts_value() -> None:
    obs = ProjectTestObligations().project(
        _arch(), _problem(["When ingest_event is called, Then result is 42"]))
    crit = next(o for o in obs if "result is" in o.source)
    assert crit.kind is AssertionKind.EQUALS
    assert crit.detail == "42"


def test_expected_outcome_overrides_prose() -> None:
    obs = ProjectTestObligations().project(
        _arch(),
        _problem(["When ingest_event is called, Then something vague happens"],
                 (ExpectedOutcome("ingest_event", "equals", "7"),)))
    crit = next(o for o in obs if "vague" in o.source)
    assert crit.kind is AssertionKind.EQUALS
    assert crit.detail == "7"


def test_invariant_becomes_constructor_raises_obligation() -> None:
    obs = ProjectTestObligations().project(_arch(), _problem([]))
    inv = [o for o in obs if o.target_class == "RawBody"]
    assert len(inv) == 1
    assert inv[0].kind is AssertionKind.RAISES
    assert inv[0].method == "<init>"


def test_unresolvable_verb_is_skipped() -> None:
    obs = ProjectTestObligations().project(
        _arch(), _problem(["When frobnicate is called, Then it works"]))
    assert not any(o.source.startswith("When frobnicate") for o in obs)
