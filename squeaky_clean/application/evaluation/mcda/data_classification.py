"""DataClassification DTO: per-field sensitivity tag."""

from dataclasses import dataclass

_VALID_SENSITIVITIES: frozenset[str] = frozenset({
    "public", "pii", "credential", "session_token", "audit",
})


@dataclass(frozen=True)
class DataClassification:
    """Declares the sensitivity classification of one field."""

    field_ref: str
    sensitivity: str

    def __post_init__(self) -> None:
        """Reject malformed field_ref or unknown sensitivity."""
        if "." not in self.field_ref:
            raise ValueError(
                f"DataClassification.field_ref {self.field_ref!r} must look "
                "like 'Class.field'"
            )
        cls, _, fld = self.field_ref.partition(".")
        if not cls or not fld:
            raise ValueError(
                f"DataClassification.field_ref {self.field_ref!r} must look "
                "like 'Class.field'"
            )
        if self.sensitivity not in _VALID_SENSITIVITIES:
            raise ValueError(
                f"DataClassification.sensitivity {self.sensitivity!r} not in "
                f"{sorted(_VALID_SENSITIVITIES)}"
            )
