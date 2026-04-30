"""TechSpecOperation DTO: one entry in TechSpec.primary_operations."""

from dataclasses import dataclass

_VALID_IDEMPOTENCY: frozenset[str] = frozenset(
    {"idempotent", "non_idempotent", "conditional"}
)


@dataclass(frozen=True)
class TechSpecOperation:
    """One SDK operation a Tier C ICP must implement."""

    name: str
    signature: str
    sdk_call: str
    error_types: tuple[str, ...]
    idempotency: str
    retry_policy: str = "none"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("TechSpecOperation.name is empty")
        if not self.signature:
            raise ValueError(f"{self.name}: signature is empty")
        if not self.sdk_call:
            raise ValueError(f"{self.name}: sdk_call is empty")
        if not self.error_types:
            raise ValueError(f"{self.name}: error_types is empty")
        if self.idempotency not in _VALID_IDEMPOTENCY:
            raise ValueError(
                f"{self.name}: idempotency must be one of "
                f"{sorted(_VALID_IDEMPOTENCY)}, got {self.idempotency!r}"
            )
