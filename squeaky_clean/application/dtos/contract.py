"""Contract DTO: cross-service payload contract bound to a transport."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.application.dtos.contract_field import ContractField


@dataclass(frozen=True)
class Contract:
    """Cross-service payload contract: name, transport, fields, producer id.

    Used by the ContractFidelity subsystem to ensure consumer services
    declare entities whose fields exactly match producer payloads.
    """

    name: str
    transport: str
    fields: tuple[ContractField, ...]
    producer_problem_id: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Contract.name must be non-empty")
        if not self.transport:
            raise ValueError("Contract.transport must be non-empty")

    def required_field_names(self) -> frozenset[str]:
        """Return the set of field names where required=True."""
        return frozenset(f.name for f in self.fields if f.required)

    def all_field_names(self) -> frozenset[str]:
        """Return the set of all field names (required or not)."""
        return frozenset(f.name for f in self.fields)
