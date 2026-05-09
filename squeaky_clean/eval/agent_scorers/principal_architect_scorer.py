"""Scores PrincipalArchitect §Notation output against structural rules."""

from __future__ import annotations

from squeaky_clean.application.use_cases.parse_notation import ParseNotation
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.eval.agent_scorers.agent_score import AgentScore


class PrincipalArchitectScorer:
    """Scores raw §Notation text on parse, validate, and self-consistency."""

    def __init__(self) -> None:
        self._parser: ParseNotation = ParseNotation()

    def score(self, fixture_id: str, raw_notation: str) -> AgentScore:
        """Return AgentScore with structural_pass in [0,1] and issues list."""
        issues: list[str] = []
        try:
            spec = self._parser.parse(raw_notation)
        except NotationParseError as exc:
            return AgentScore(
                agent="PrincipalArchitect", fixture=fixture_id,
                parsed=False, structural_pass=0.0,
                issues=(f"parse error: {exc}",),
            )
        for v in spec.validate():
            issues.append(f"validation: {v}")
        declared = {c.name for c in spec.classes}
        for c in spec.classes:
            for dep in c.depends:
                if dep not in declared:
                    issues.append(
                        f"class {c.name!r} depends on undeclared {dep!r}"
                    )
            for con in c.concretes:
                if con not in declared:
                    issues.append(
                        f"class {c.name!r} has undeclared concrete {con!r}"
                    )
        if spec.name == "":
            issues.append("module name is empty")
        if not spec.classes:
            issues.append("no classes declared")
        score = 0.0 if issues else 1.0
        return AgentScore(
            agent="PrincipalArchitect", fixture=fixture_id,
            parsed=True, structural_pass=score, issues=tuple(issues),
        )
