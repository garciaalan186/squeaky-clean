"""Manager-tier fallback call helper for TechSpecComposer (H2)."""

from __future__ import annotations

import json

from squeaky_clean.application.generation.techspec.composition_failure import CompositionFailure
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_SYSTEM_PROMPT = "You repair TechSpec JSON or flag un_implementable."


class TechSpecComposerManagerCall:
    """Encapsulates the Manager-tier LLM call + response parsing."""

    def __init__(
        self, gateway: LLMGateway, routing: ModelRoutingPolicy,
        *, logger: RunLogger | None = None,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._routing: ModelRoutingPolicy = routing
        self._log: RunLogger = logger or NullRunLogger()

    def request_correction(
        self, failure: CompositionFailure,
    ) -> dict[str, object] | None:
        """Return parsed correction dict, or None on un_implementable / parse fail."""
        request = LLMRequest(
            model=self._routing.route(ModelTier.MANAGER),
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=self._build_prompt(failure), tier="manager",
        )
        return self._parse(self._gateway.complete(request).content)

    def _build_prompt(self, failure: CompositionFailure) -> str:
        cls = failure.assignment.class_spec
        return (
            "Validation errors:\n  - " + "\n  - ".join(failure.errors) +
            f"\nClassSpec: name={cls.name} methods={list(cls.methods)}"
            f" depends={list(cls.depends)}"
            f"\nTechSpec.primary_operations="
            f"{[op.name for op in failure.tech_spec.primary_operations]}"
            "\nReturn JSON: either {\"tech_spec\": <full TechSpec dict>}"
            " or {\"un_implementable\": true}."
        )

    def _parse(self, raw: str) -> dict[str, object] | None:
        """Parse the Manager reply; None = un_implementable / unusable reply.

        None is meaningful (caller marks the class un-implementable); an
        unusable reply is logged via the injected RunLogger (R6.8)."""
        text = (raw or "").strip()
        if not text:
            self._log.event("manager_correction_empty_reply")
            return None  # unusable reply — logged above, caller keeps original spec
        if '"un_implementable": true' in text:
            return None  # R6.8-legit: explicit Manager verdict, not an error
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            self._log.event("manager_correction_no_json", head=text[:120])
            return None  # unusable reply — logged above
        parsed: object = None
        try:
            parsed = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            self._log.event("manager_correction_unparseable", error=str(exc))
        if not isinstance(parsed, dict):
            if parsed is not None:  # decode failures already logged above
                self._log.event(
                    "manager_correction_not_object", got=type(parsed).__name__,
                )
            return None  # unusable reply — logged above
        if parsed.get("un_implementable") is True:
            return None  # R6.8-legit: explicit Manager verdict, not an error
        return parsed.get("tech_spec") if "tech_spec" in parsed else parsed
