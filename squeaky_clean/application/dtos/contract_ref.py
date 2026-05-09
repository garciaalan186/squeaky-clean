"""ContractRef DTO: reference to a Contract by name + role (produces|consumes)."""

from __future__ import annotations

from dataclasses import dataclass

_VALID_ROLES: frozenset[str] = frozenset({"produces", "consumes"})


@dataclass(frozen=True)
class ContractRef:
    """Reference to a Contract registered in the ContractRegistry."""

    contract_name: str
    role: str

    def __post_init__(self) -> None:
        if not self.contract_name:
            raise ValueError("ContractRef.contract_name must be non-empty")
        if self.role not in _VALID_ROLES:
            raise ValueError(
                f"ContractRef.role must be one of {sorted(_VALID_ROLES)}; "
                f"got {self.role!r}"
            )
