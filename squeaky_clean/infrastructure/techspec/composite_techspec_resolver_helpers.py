"""Helpers for CompositeTechSpecResolver — kept separate to honor file caps."""

import json
from dataclasses import dataclass
from typing import cast

from squeaky_clean.application.generation.techspec.tech_spec_html_extractor import (
    TechSpecHTMLExtractor,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_resolution import TechSpecResolution
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget
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
) -> TechSpecResolution:
    """Convert raw payload to a validated TechSpec, or a reasoned failure.

    Never returns None: an unusable payload comes back as
    ``TechSpecFetchFailed(reason)`` so the resolver can log it (R6.8).
    """
    if is_html:
        draft = extractor.extract(payload, TechSpecTarget(
            category=attempt.category, technology=attempt.technology,
            version_pin=attempt.version,
        ))
    else:
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            return TechSpecFetchFailed("payload is not a JSON object")
        draft = cast(dict[str, object], parsed)
    violations = validator.validate(draft)
    if violations:
        return TechSpecFetchFailed(f"schema violations: {violations}")
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
