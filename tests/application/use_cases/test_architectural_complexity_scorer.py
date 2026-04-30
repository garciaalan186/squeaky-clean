"""Tests for ArchitecturalComplexityScorer (ACS — see BENCHMARK_METHODOLOGY.md)."""

from __future__ import annotations

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.dtos.contract_ref import ContractRef
from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.architectural_complexity_scorer import (
    ArchitecturalComplexityScorer,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _problem(**overrides: object) -> ProblemSpec:
    base = {
        "id": "P0", "tier": 0, "slug": "calc",
        "description": "x", "required_bounded_contexts": ["Calc"],
        "acceptance_criteria": ["a", "b", "c", "d"],
        "expected_module_count": (1, 1), "expected_class_count": (3, 5),
        "required_patterns": ["Entity"],
        "target_language": TargetLanguage.PYTHON,
    }
    base.update(overrides)
    return ProblemSpec(**base)  # type: ignore[arg-type]


def _arch(modules: int = 1, classes_per: int = 4) -> ArchitectureSpec:
    out = []
    for i in range(modules):
        cs = tuple(
            ClassSpec(name=f"C{i}_{j}", pattern="Entity", implements=None,
                      methods=(), depends=(), concretes=(),
                      fields=("id: str",), invariants=())
            for j in range(classes_per)
        )
        out.append(ModuleSpec(
            name=f"M{i}", layer=LayerType.DOMAIN, exports=(f"C{i}_0",),
            depends=(), classes=cs, invariants=(),
        ))
    return ArchitectureSpec(modules=tuple(out), graph=ArchitectureGraph(edges={}))


def test_baseline_calculator_yields_acs_near_one() -> None:
    score = ArchitecturalComplexityScorer().score(_problem(), _arch())
    assert 0.5 <= score.normalized <= 2.0


def test_more_modules_increases_structural() -> None:
    s1 = ArchitecturalComplexityScorer().score(_problem(), _arch(modules=1)).structural
    s5 = ArchitecturalComplexityScorer().score(_problem(), _arch(modules=5)).structural
    assert s5 > s1


def test_more_acceptance_criteria_increases_constraint() -> None:
    p_few = _problem(acceptance_criteria=["a"])
    p_many = _problem(acceptance_criteria=["a"] * 20)
    s_few = ArchitecturalComplexityScorer().score(p_few, _arch()).constraint
    s_many = ArchitecturalComplexityScorer().score(p_many, _arch()).constraint
    assert s_many > s_few


def test_infrastructure_choices_inflate_constraint() -> None:
    p_no = _problem()
    p_yes = _problem(infrastructure_choices=(
        InfrastructureChoice(category="blob_storage", technology="s3",
                             version_pin="boto3==1.34"),
    ))
    s_no = ArchitecturalComplexityScorer().score(p_no, _arch()).constraint
    s_yes = ArchitecturalComplexityScorer().score(p_yes, _arch()).constraint
    assert s_yes > s_no


def test_contracts_inflate_constraint() -> None:
    p_no = _problem()
    p_yes = _problem(produces_contracts=(
        Contract(name="c", transport="kafka:c",
                 fields=(ContractField(name="id", type="str"),)),
    ), consumes_contracts=(ContractRef(contract_name="c", role="consumes"),))
    a = ArchitecturalComplexityScorer().score(p_no, _arch()).constraint
    b = ArchitecturalComplexityScorer().score(p_yes, _arch()).constraint
    assert b > a


def test_data_classification_inflates_constraint() -> None:
    p_yes = _problem(data_classification=(
        DataClassification(field_ref="X.y", sensitivity="pii"),
    ))
    a = ArchitecturalComplexityScorer().score(_problem(), _arch()).constraint
    b = ArchitecturalComplexityScorer().score(p_yes, _arch()).constraint
    assert b > a


def test_components_dict_carries_raw_dimensions() -> None:
    score = ArchitecturalComplexityScorer().score(_problem(), _arch())
    for k in ("M", "C", "D", "X", "I", "H", "N", "V", "E",
              "A", "CC", "DC", "IC"):
        assert k in score.components


def test_codegen_zero_when_source_dir_missing() -> None:
    score = ArchitecturalComplexityScorer().score(
        _problem(), _arch(), source_dir=None,
    )
    assert score.codegen == 0.0


def test_normalized_scales_with_composite() -> None:
    small = ArchitecturalComplexityScorer().score(_problem(), _arch(modules=1))
    big = ArchitecturalComplexityScorer().score(_problem(), _arch(modules=8))
    assert big.normalized > small.normalized
