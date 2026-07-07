"""LoadProblemSpecFromFile: build a ProblemSpec from a user JSON/YAML file."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.entity_lifecycle import EntityLifecycle, StateTransition
from squeaky_clean.application.dtos.expected_outcome import ExpectedOutcome
from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.query_semantic import QuerySemantic
from squeaky_clean.application.use_cases.load_contracts_from_problem import (
    parse_consumes,
    parse_produces,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class LoadProblemSpecFromFile:
    """Read a JSON file describing a ProblemSpec and validate its shape."""

    def load(self, path: Path) -> ProblemSpec:
        """Return a ProblemSpec parsed from the JSON at ``path``."""
        raw = json.loads(path.read_text())
        if not isinstance(raw, dict):
            raise ValueError(f"{path} must contain a JSON object")
        d = cast(dict[str, object], raw)
        gs: Callable[[str], list[object]] = lambda k: cast(  # noqa: E731
            list[object], d.get(k) or [])
        return ProblemSpec(
            id=str(d.get("id") or ""),
            tier=int(cast(int, d.get("tier", 0))),
            slug=str(d.get("slug") or ""),
            description=str(d.get("description") or ""),
            required_bounded_contexts=[str(c) for c in gs("required_bounded_contexts")],
            acceptance_criteria=[str(c) for c in gs("acceptance_criteria")],
            expected_module_count=self._pair(
                cast(list[int], d.get("expected_module_count") or [1, 1])),
            expected_class_count=self._pair(
                cast(list[int], d.get("expected_class_count") or [3, 6])),
            required_patterns=[str(p) for p in gs("required_patterns")],
            target_language=TargetLanguage(
                str(d.get("target_language") or "python")),
            domain_conventions=tuple(str(c) for c in gs("domain_conventions")),
            query_semantics=tuple(
                QuerySemantic(use_case=str(i.get("use_case") or ""),
                              shape=str(i.get("shape") or ""))
                for i in cast(list[dict[str, object]], d.get("query_semantics") or [])),
            entity_lifecycle=tuple(
                EntityLifecycle(
                    entity=str(i.get("entity") or ""),
                    transitions=tuple(
                        StateTransition(
                            from_state=str(t.get("from_state") or ""),
                            to_state=str(t.get("to_state") or ""),
                            trigger=str(t.get("trigger") or ""))
                        for t in cast(list[dict[str, object]], i.get("transitions") or [])))
                for i in cast(list[dict[str, object]], d.get("entity_lifecycle") or [])),
            data_classification=tuple(
                DataClassification(
                    field_ref=str(i.get("field_ref") or ""),
                    sensitivity=str(i.get("sensitivity") or ""))
                for i in cast(list[dict[str, object]], d.get("data_classification") or [])),
            infrastructure_choices=tuple(
                InfrastructureChoice(
                    category=str(i.get("category") or ""),
                    technology=str(i.get("technology") or ""),
                    version_pin=str(i.get("version_pin") or ""))
                for i in cast(list[dict[str, object]], d.get("infrastructure_choices") or [])),
            mcda_weights=self._weights(d.get("mcda_weights")),
            produces_contracts=parse_produces(d.get("produces_contracts")),
            consumes_contracts=parse_consumes(d.get("consumes_contracts")),
            expected_outcomes=tuple(
                ExpectedOutcome(
                    verb=str(i.get("verb") or ""),
                    kind=str(i.get("kind") or "call_only"),
                    value=str(i.get("value") or ""))
                for i in cast(list[dict[str, object]],
                              d.get("expected_outcomes") or [])),
        )

    @staticmethod
    def _weights(raw: object) -> dict[str, float] | None:
        if raw is None:
            return None
        m = cast(dict[str, object], raw)
        return {str(k): float(cast(float, v)) for k, v in m.items()}

    def _pair(self, raw: list[int]) -> tuple[int, int]:
        a = int(raw[0]) if len(raw) > 0 else 0
        b = int(raw[1]) if len(raw) > 1 else a
        return (a, b)
