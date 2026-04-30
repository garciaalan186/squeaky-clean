"""Scores a single ICP output: parses out a class file, then validates it."""

from __future__ import annotations

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parse_implemented_class import ParseImplementedClass
from squeaky_clean.eval.agent_scorers.agent_score import AgentScore


class ICPScorer:
    """Score one ICP raw response for code-fence parse + class declaration."""

    def __init__(self) -> None:
        self._parser: ParseImplementedClass = ParseImplementedClass()

    def score(
        self, fixture_id: str, raw: str, expected_class: str,
    ) -> AgentScore:
        """Return AgentScore checking fenced-code parse + class presence."""
        try:
            code = self._parser.parse(raw, expected_class)
        except ImplementedClassParseError as exc:
            return AgentScore(
                agent="ICP", fixture=fixture_id,
                parsed=False, structural_pass=0.0,
                issues=(f"parse error: {exc}",),
            )
        issues: list[str] = []
        if expected_class not in code:
            issues.append(f"emitted code missing class {expected_class!r}")
        if len(code.splitlines()) > 80:
            issues.append("file exceeds 80-line cap")
        if "TODO" in code or "FIXME" in code:
            issues.append("contains TODO/FIXME placeholder")
        score = 0.0 if issues else 1.0
        return AgentScore(
            agent="ICP", fixture=fixture_id,
            parsed=True, structural_pass=score, issues=tuple(issues),
        )
