"""Manager-tier fallback call helper for TechSpecComposer (H2)."""

from __future__ import annotations

import json

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest

_MANAGER_MODEL = "claude-sonnet-4-6"
_SYSTEM_PROMPT = "You repair TechSpec JSON or flag un_implementable."


class TechSpecComposerManagerCall:
    """Encapsulates the Manager-tier LLM call + response parsing."""

    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway: LLMGateway = gateway

    def request_correction(
        self, assignment: ClassAssignment, tech_spec: TechSpec,
        errors: tuple[str, ...],
    ) -> dict[str, object] | None:
        """Return parsed correction dict, or None on un_implementable / parse fail."""
        prompt = self._build_prompt(assignment, tech_spec, errors)
        request = LLMRequest(
            model=_MANAGER_MODEL, system_prompt=_SYSTEM_PROMPT,
            user_prompt=prompt, tier="manager",
        )
        return self._parse(self._gateway.complete(request).content)

    def _build_prompt(
        self, assignment: ClassAssignment, tech_spec: TechSpec,
        errors: tuple[str, ...],
    ) -> str:
        cls = assignment.class_spec
        return (
            "Validation errors:\n  - " + "\n  - ".join(errors) +
            f"\nClassSpec: name={cls.name} methods={list(cls.methods)}"
            f" depends={list(cls.depends)}"
            f"\nTechSpec.primary_operations="
            f"{[op.name for op in tech_spec.primary_operations]}"
            "\nReturn JSON: either {\"tech_spec\": <full TechSpec dict>}"
            " or {\"un_implementable\": true}."
        )

    def _parse(self, raw: str) -> dict[str, object] | None:
        text = (raw or "").strip()
        if not text or '"un_implementable": true' in text:
            return None
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict) or parsed.get("un_implementable") is True:
            return None
        return parsed.get("tech_spec") if "tech_spec" in parsed else parsed
