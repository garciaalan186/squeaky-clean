"""Tests for ContractRegistry: lookup miss, register+lookup, all_contracts."""

from pathlib import Path

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry


def _c(name: str, fields: tuple[ContractField, ...] = ()) -> Contract:
    fs = fields or (ContractField(name="id", type="str"),)
    return Contract(name=name, transport="kafka:t", fields=fs)


def test_lookup_returns_none_when_unregistered(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    assert reg.lookup("nope") is None


def test_register_then_lookup_round_trip(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(_c("events.raw", (
        ContractField(name="id", type="str"),
        ContractField(name="payload", type="str"),
    )))
    fresh = ContractRegistry(tmp_path)
    found = fresh.lookup("events.raw")
    assert found is not None
    assert found.transport == "kafka:t"
    assert {f.name for f in found.fields} == {"id", "payload"}


def test_register_writes_path_under_root(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    path = reg.register(_c("alpha"))
    assert path == tmp_path / "alpha.json"
    assert path.is_file()


def test_all_contracts_returns_sorted_by_filename(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(_c("zeta"))
    reg.register(_c("alpha"))
    reg.register(_c("mid"))
    names = [c.name for c in reg.all_contracts()]
    assert names == sorted(names)


def test_all_contracts_empty_when_root_missing(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path / "missing")
    assert reg.all_contracts() == ()


def test_register_records_producer_problem_id(tmp_path: Path) -> None:
    reg = ContractRegistry(tmp_path)
    reg.register(Contract(
        name="evt", transport="kafka:t",
        fields=(ContractField(name="id", type="str"),),
        producer_problem_id="EVENT_PRODUCER"))
    found = reg.lookup("evt")
    assert found is not None
    assert found.producer_problem_id == "EVENT_PRODUCER"
