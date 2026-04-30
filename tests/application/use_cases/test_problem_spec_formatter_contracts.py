"""ProblemSpecFormatter: ProducesContracts / ConsumesContracts rendering."""

from pathlib import Path

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.dtos.contract_ref import ContractRef
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry
from squeaky_clean.application.use_cases.problem_spec_formatter import (
    ProblemSpecFormatter,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _spec(**kw: object) -> ProblemSpec:
    base: dict[str, object] = dict(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=["x"], acceptance_criteria=["a"],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=["Entity"], target_language=TargetLanguage.PYTHON,
    )
    base.update(kw)
    return ProblemSpec(**base)  # type: ignore[arg-type]


def _contract() -> Contract:
    return Contract(name="events.raw", transport="kafka:events.raw", fields=(
        ContractField(name="id", type="str"),
        ContractField(name="payload", type="str"),
    ))


def test_renders_produces_contracts_section(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    fmt = ProblemSpecFormatter(reg)
    spec = _spec(produces_contracts=(_contract(),))
    out = fmt.format(spec)
    assert "ProducesContracts:" in out
    assert "events.raw via kafka:events.raw" in out
    assert "id: str" in out
    assert "payload: str" in out


def test_renders_consumes_with_resolved_fields(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(_contract())
    fmt = ProblemSpecFormatter(reg)
    spec = _spec(consumes_contracts=(
        ContractRef(contract_name="events.raw", role="consumes"),))
    out = fmt.format(spec)
    assert "ConsumesContracts:" in out
    assert "events.raw via kafka:events.raw" in out
    assert "payload: str" in out


def test_renders_consumes_marks_unregistered(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    fmt = ProblemSpecFormatter(reg)
    spec = _spec(consumes_contracts=(
        ContractRef(contract_name="events.raw", role="consumes"),))
    out = fmt.format(spec)
    assert "events.raw: NOT_REGISTERED" in out


def test_omits_contract_sections_when_empty(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    fmt = ProblemSpecFormatter(reg)
    out = fmt.format(_spec())
    assert "ProducesContracts:" not in out
    assert "ConsumesContracts:" not in out
