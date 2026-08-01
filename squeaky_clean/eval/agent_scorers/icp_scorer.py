"""Scores a single ICP output: parses out a class file, then validates it."""

from __future__ import annotations

from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)
from squeaky_clean.eval.agent_scorers.agent_score import AgentScore


class ICPScorer:
    """Score ICP raw responses for code-fence parse + class declaration.

    Constructed per oracle: ``expected_class`` is the class every scored
    fixture is expected to declare.
    """

    def __init__(self, expected_class: str) -> None:
        self._expected: str = expected_class
        self._parser: ParseImplementedClass = ParseImplementedClass()

    def score(self, fixture_id: str, raw: str) -> AgentScore:
        """Return AgentScore checking fenced-code parse + class presence."""
        expected_class = self._expected
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
