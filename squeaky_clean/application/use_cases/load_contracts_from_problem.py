"""load_contracts_from_problem: parse produces/consumes contracts from raw JSON."""

from __future__ import annotations

from typing import cast

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField
from squeaky_clean.application.dtos.contract_ref import ContractRef


def parse_produces(raw: object) -> tuple[Contract, ...]:
    """Parse a list of produced Contract dicts from a ProblemSpec JSON file."""
    if raw is None:
        return ()
    items = cast(list[dict[str, object]], raw)
    out: list[Contract] = []
    for it in items:
        fraw = cast(list[dict[str, object]], it.get("fields") or [])
        fields = tuple(
            ContractField(name=str(f.get("name") or ""),
                          type=str(f.get("type") or ""),
                          required=bool(f.get("required", True)))
            for f in fraw)
        producer = it.get("producer_problem_id")
        out.append(Contract(
            name=str(it.get("name") or ""),
            transport=str(it.get("transport") or ""),
            fields=fields,
            producer_problem_id=str(producer) if producer else None))
    return tuple(out)


def parse_consumes(raw: object) -> tuple[ContractRef, ...]:
    """Parse a list of consumed ContractRef dicts from a ProblemSpec JSON file."""
    if raw is None:
        return ()
    items = cast(list[dict[str, object]], raw)
    return tuple(
        ContractRef(contract_name=str(it.get("contract_name") or ""),
                    role=str(it.get("role") or "consumes"))
        for it in items)
