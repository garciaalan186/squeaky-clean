"""ProjectTestObligations: derive a deterministic test contract from the spec.

The Squib + acceptance criteria ARE the test's intent; this projects them
into a set of TestObligations so verification is a pure function of the
spec, not a fuzzy read of the (possibly-gamed) test. Structure — which
class, which method, which assertion kind — is deterministic from the
current §Notation; the value is deterministic when an ``expected_outcomes``
entry is present, else parsed from the Then clause.
"""

from __future__ import annotations

import re

from squeaky_clean.application.dtos.expected_outcome import ExpectedOutcome
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.test_obligation import TestObligation
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind

_WHEN = re.compile(r"\bWhen\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_THEN = re.compile(r"\bThen\b(.*)$", re.IGNORECASE | re.DOTALL)
_RAISES = re.compile(r"error is raised|raise|rejected|throw|invalid", re.IGNORECASE)
_EQUALS = re.compile(
    r"result is\s+(\S+)|returns?\s+(\S+)|equals?\s+(\S+)", re.IGNORECASE)
_FIELD = re.compile(r"contain|with keys|holds|includes", re.IGNORECASE)
_CTOR: str = "<init>"


def _normalize(token: str) -> str:
    return token.replace("_", "").lower()


class ProjectTestObligations:
    """Projects (ArchitectureSpec, ProblemSpec) -> a TestObligation contract."""

    def project(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> tuple[TestObligation, ...]:
        """Return the deterministic obligation set for ``problem`` on ``arch``."""
        index = self._verb_index(arch)
        outcomes = {_normalize(o.verb): o for o in problem.expected_outcomes}
        out: list[TestObligation] = []
        for crit in problem.acceptance_criteria:
            ob = self._from_criterion(crit, index, outcomes)
            if ob is not None:
                out.append(ob)
        out.extend(self._from_invariants(arch))
        return tuple(out)

    @staticmethod
    def _verb_index(arch: ArchitectureSpec) -> dict[str, tuple[str, str]]:
        index: dict[str, tuple[str, str]] = {}
        for module in arch.modules:
            for cls in module.classes:
                for method in cls.methods:
                    name = method.split("(", 1)[0].strip()
                    index.setdefault(_normalize(name), (cls.name, name))
        return index

    def _from_criterion(
        self, crit: str, index: dict[str, tuple[str, str]],
        outcomes: dict[str, ExpectedOutcome],
    ) -> TestObligation | None:
        m = _WHEN.search(crit)
        if m is None:
            return None
        resolved = index.get(_normalize(m.group(1)))
        if resolved is None:
            return None
        cls, method = resolved
        outcome = outcomes.get(_normalize(m.group(1)))
        kind, detail = (
            (AssertionKind(outcome.kind), outcome.value) if outcome is not None
            else self._then_outcome(crit))
        return TestObligation(cls, method, kind, detail, crit)

    @staticmethod
    def _then_outcome(crit: str) -> tuple[AssertionKind, str]:
        m = _THEN.search(crit)
        then = m.group(1) if m is not None else ""
        if _RAISES.search(then):
            return AssertionKind.RAISES, ""
        eq = _EQUALS.search(then)
        if eq is not None:
            return AssertionKind.EQUALS, next(g for g in eq.groups() if g)
        if _FIELD.search(then):
            return AssertionKind.FIELD_HOLDS, ""
        return AssertionKind.CALL_ONLY, ""

    @staticmethod
    def _from_invariants(arch: ArchitectureSpec) -> list[TestObligation]:
        out: list[TestObligation] = []
        for module in arch.modules:
            for cls in module.classes:
                for inv in cls.invariants:
                    out.append(TestObligation(
                        cls.name, _CTOR, AssertionKind.RAISES, inv, inv))
        return out
