"""Scores TestArchitect output against structural rules + spec consistency."""

from __future__ import annotations

from squeaky_clean.application.dtos.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.application.use_cases.parse_test_architecture import ParseTestArchitecture
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.eval.agent_scorers.agent_score import AgentScore


class TestArchitectScorer:
    """Score TestArchitect raw output for parse + spec-consistency."""

    def __init__(self) -> None:
        self._parser: ParseTestArchitecture = ParseTestArchitecture()

    def score(
        self, fixture_id: str, raw: str, module: ModuleSpec,
    ) -> AgentScore:
        """Return AgentScore checking sections + class-name coverage."""
        try:
            arch = self._parser.parse(raw)
        except TestArchitectureParseError as exc:
            return AgentScore(
                agent="TestArchitect", fixture=fixture_id,
                parsed=False, structural_pass=0.0,
                issues=(f"parse error: {exc}",),
            )
        issues: list[str] = []
        if not arch.gherkin_scenarios:
            issues.append("no Gherkin scenarios")
        declared = {c.name for c in module.classes}
        for sk in arch.test_skeletons:
            if sk.class_name not in declared:
                issues.append(
                    f"skeleton class {sk.class_name!r} not in ModuleSpec"
                )
            if "pytest.fail" in sk.code and "not implemented" in sk.code:
                issues.append(
                    f"skeleton {sk.class_name} is not-implemented stub"
                )
        score = 0.0 if issues else 1.0
        return AgentScore(
            agent="TestArchitect", fixture=fixture_id,
            parsed=True, structural_pass=score, issues=tuple(issues),
        )
