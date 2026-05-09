"""Tests for Contract / ContractField / ContractRef DTO validation."""

import pytest

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.dtos.contract_ref import ContractRef


def test_contract_field_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        ContractField(name="", type="str")


def test_contract_field_rejects_empty_type() -> None:
    with pytest.raises(ValueError, match="type"):
        ContractField(name="payload", type="")


def test_contract_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Contract(name="", transport="kafka:t",
                 fields=(ContractField(name="x", type="str"),))


def test_contract_rejects_empty_transport() -> None:
    with pytest.raises(ValueError, match="transport"):
        Contract(name="X", transport="",
                 fields=(ContractField(name="x", type="str"),))


def test_contract_required_field_names_filters_optional() -> None:
    c = Contract(name="X", transport="kafka:t", fields=(
        ContractField(name="a", type="str"),
        ContractField(name="b", type="int", required=False),
    ))
    assert c.required_field_names() == frozenset({"a"})
    assert c.all_field_names() == frozenset({"a", "b"})


def test_contract_ref_rejects_invalid_role() -> None:
    with pytest.raises(ValueError, match="role"):
        ContractRef(contract_name="X", role="emits")


def test_contract_ref_rejects_empty_contract_name() -> None:
    with pytest.raises(ValueError, match="contract_name"):
        ContractRef(contract_name="", role="produces")


def test_contract_ref_accepts_produces_and_consumes() -> None:
    assert ContractRef(contract_name="X", role="produces").role == "produces"
    assert ContractRef(contract_name="X", role="consumes").role == "consumes"
