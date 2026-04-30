"""TechSpecBuilder: convert a validated raw dict into a TechSpec dataclass."""

from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation


class TechSpecBuilder:
    """Pure-Python builder mapping raw JSON dicts to TechSpec value objects."""

    def build(self, raw: dict[str, object]) -> TechSpec:
        """Return a frozen TechSpec from a schema-validated raw dict."""
        return TechSpec(
            schema_version=str(raw.get("schema_version") or ""),
            category=str(raw.get("category") or ""),
            technology=str(raw.get("technology") or ""),
            version_pin=str(raw.get("version_pin") or ""),
            language=str(raw.get("language") or ""),
            install=cast(dict[str, str], raw.get("install") or {}),
            imports=cast(dict[str, object], raw.get("imports") or {}),
            client_construction=cast(
                dict[str, object], raw.get("client_construction") or {}
            ),
            primary_operations=self._ops(raw),
            auth=cast(dict[str, object], raw.get("auth") or {}),
            observability_hooks=tuple(
                str(h) for h in cast(
                    list[object], raw.get("observability_hooks") or []
                )
            ),
            rate_limit_defaults=cast(
                dict[str, int], raw.get("rate_limit_defaults") or {}
            ),
            code_style_notes=tuple(
                str(s) for s in cast(
                    list[object], raw.get("code_style_notes") or []
                )
            ),
            allowed_doc_origins=tuple(
                str(o) for o in cast(
                    list[object], raw.get("allowed_doc_origins") or []
                )
            ),
        )

    def _ops(self, raw: dict[str, object]) -> tuple[TechSpecOperation, ...]:
        ops_raw = cast(
            list[dict[str, object]], raw.get("primary_operations") or []
        )
        return tuple(
            TechSpecOperation(
                name=str(o.get("name") or ""),
                signature=str(o.get("signature") or ""),
                sdk_call=str(o.get("sdk_call") or ""),
                error_types=tuple(
                    str(e) for e in cast(
                        list[object], o.get("error_types") or []
                    )
                ),
                idempotency=str(o.get("idempotency") or ""),
                retry_policy=str(o.get("retry_policy") or "none"),
            )
            for o in ops_raw
        )
