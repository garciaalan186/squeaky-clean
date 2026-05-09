"""TechSpec DTO: validated SDK contract bundle for one (category,tech,version)."""

from dataclasses import dataclass, field

from squeaky_clean.application.dtos.infrastructure_category import (
    ALL_INFRASTRUCTURE_CATEGORIES,
)
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation

_VALID_LANGUAGES: frozenset[str] = frozenset(
    {"python", "javascript", "typescript", "java", "go", "rust"}
)


@dataclass(frozen=True)
class TechSpec:
    """Frozen, schema-validated TechSpec value object (design doc §6.1)."""

    schema_version: str
    category: str
    technology: str
    version_pin: str
    language: str
    install: dict[str, str]
    imports: dict[str, object]
    client_construction: dict[str, object]
    primary_operations: tuple[TechSpecOperation, ...]
    auth: dict[str, object]
    observability_hooks: tuple[str, ...] = ()
    rate_limit_defaults: dict[str, int] = field(default_factory=dict)
    code_style_notes: tuple[str, ...] = ()
    allowed_doc_origins: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != "v1":
            raise ValueError(
                f"unsupported TechSpec schema_version: {self.schema_version!r}"
            )
        if self.category not in ALL_INFRASTRUCTURE_CATEGORIES:
            raise ValueError(f"unknown category: {self.category!r}")
        if self.language not in _VALID_LANGUAGES:
            raise ValueError(f"unknown language: {self.language!r}")
        if not self.primary_operations:
            raise ValueError("TechSpec.primary_operations must not be empty")
