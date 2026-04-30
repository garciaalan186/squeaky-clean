"""Helpers for CompositeTechSpecResolver — kept separate to honor file caps."""

import json
from dataclasses import dataclass
from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.tech_spec_html_extractor import (
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder

AllowlistRegistry = dict[tuple[str, str], tuple[str, ...]]


@dataclass(frozen=True)
class FetchAttempt:
    """Identifies the (category, technology, version) being fetched."""

    category: str
    technology: str
    version: str


def build_from_payload(
    payload: str, attempt: FetchAttempt, is_html: bool,
    extractor: TechSpecHTMLExtractor, validator: TechSpecValidator,
) -> TechSpec | None:
    """Convert raw payload to validated TechSpec or return None on failure."""
    if is_html:
        draft = extractor.extract(
            payload, attempt.category, attempt.technology, attempt.version,
        )
    else:
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            return None
        draft = cast(dict[str, object], parsed)
    if validator.validate(draft):
        return None
    return TechSpecBuilder().build(draft)


def spec_to_dict(spec: TechSpec, clean: str, is_html: bool) -> dict[str, object]:
    """Serialize TechSpec back to dict for cache write."""
    if not is_html:
        loaded = json.loads(clean)
        if isinstance(loaded, dict):
            return cast(dict[str, object], loaded)
    return {
        "schema_version": spec.schema_version, "category": spec.category,
        "technology": spec.technology, "version_pin": spec.version_pin,
        "language": spec.language, "install": spec.install,
        "imports": spec.imports,
        "client_construction": spec.client_construction,
        "primary_operations": [
            {
                "name": op.name, "signature": op.signature,
                "sdk_call": op.sdk_call,
                "error_types": list(op.error_types),
                "idempotency": op.idempotency,
                "retry_policy": op.retry_policy,
            } for op in spec.primary_operations
        ],
        "auth": spec.auth,
    }
