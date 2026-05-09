"""Tests for validate_contract_fidelity (Subsystem 1)."""

from pathlib import Path

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.dtos.contract_ref import ContractRef
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry
from squeaky_clean.application.use_cases.validate_contract_fidelity import (
    validate_contract_fidelity,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_FIELDS = ("id: str", "received_at: str", "headers: dict[str, str]",
           "payload: str")


def _contract(name: str = "events.raw") -> Contract:
    return Contract(name=name, transport="kafka:events.raw", fields=(
        ContractField(name="id", type="str"),
        ContractField(name="received_at", type="str"),
        ContractField(name="headers", type="dict[str, str]"),
        ContractField(name="payload", type="str"),
    ))


def _arch(fields: tuple[str, ...]) -> ArchitectureSpec:
    cls = ClassSpec(name="ConsumedEvent", pattern="Entity", implements=None,
                    methods=(), depends=(), concretes=(), fields=fields)
    module = ModuleSpec(name="Consumption", layer=LayerType.DOMAIN,
                        exports=("ConsumedEvent",), depends=(),
                        classes=(cls,), invariants=())
    return ArchitectureSpec(modules=(module,),
                            graph=ArchitectureGraph(edges={}))


def _problem(**kw: object) -> ProblemSpec:
    base: dict[str, object] = dict(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=["x"], acceptance_criteria=["a"],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["Entity"], target_language=TargetLanguage.PYTHON,
    )
    base.update(kw)
    return ProblemSpec(**base)  # type: ignore[arg-type]


def test_clean_when_consumed_contract_fully_covered(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(_contract())
    arch = _arch(_FIELDS)
    p = _problem(consumes_contracts=(
        ContractRef(contract_name="events.raw", role="consumes"),))
    assert validate_contract_fidelity(arch, p, reg) == ()


def test_violation_when_consumed_contract_not_registered(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    arch = _arch(_FIELDS)
    p = _problem(consumes_contracts=(
        ContractRef(contract_name="events.raw", role="consumes"),))
    out = validate_contract_fidelity(arch, p, reg)
    assert len(out) == 1
    assert "not registered" in out[0]


def test_violation_when_entity_missing_required_field(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(_contract())
    arch = _arch(("id: str", "received_at: str", "payload: str"))  # no headers
    p = _problem(consumes_contracts=(
        ContractRef(contract_name="events.raw", role="consumes"),))
    out = validate_contract_fidelity(arch, p, reg)
    assert any("headers" in v for v in out)


def test_violation_when_no_producing_entity(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    arch = _arch(("id: str",))  # entity without all produced fields
    p = _problem(produces_contracts=(_contract(),))
    out = validate_contract_fidelity(arch, p, reg)
    assert len(out) == 1
    assert "produced contract" in out[0]


def test_clean_when_produced_entity_covers_all_fields(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    arch = _arch(_FIELDS)
    p = _problem(produces_contracts=(_contract(),))
    assert validate_contract_fidelity(arch, p, reg) == ()
