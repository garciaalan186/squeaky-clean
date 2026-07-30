"""ContractField DTO: one named field in a cross-service Contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractField:
    """One field in a cross-service contract: name, type, optional flag."""

    name: str
    type: str
    required: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("ContractField.name must be non-empty")
        if not self.type:
            raise ValueError("ContractField.type must be non-empty")
