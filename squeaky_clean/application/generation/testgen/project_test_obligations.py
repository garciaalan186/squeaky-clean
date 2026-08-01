"""ProjectTestObligations: derive a deterministic test contract from the spec.

The Squib + acceptance criteria ARE the test's intent; this projects them
into a set of TestObligations so verification is a pure function of the
spec, not a fuzzy read of the (possibly-gamed) test. Structure — which
class, which method, which assertion kind — is deterministic from the
current §Notation; the value is deterministic when an ``expected_outcomes``
entry is present, else parsed from the Then clause.
"""

from __future__ import annotations

from squeaky_clean.application.generation.testgen.obligation_lexicon import (
    is_validation_invariant,
    normalize,
    then_outcome,
    when_verb,
)
from squeaky_clean.application.generation.testgen.test_obligation import TestObligation
from squeaky_clean.application.shared.mcda.expected_outcome import ExpectedOutcome
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind
from squeaky_clean.domain.value_objects.layer_type import LayerType

_CTOR: str = "<init>"
# Only these patterns enforce their invariants in a constructor (and can be
# instantiated). A Gateway/Adapter/UseCase invariant is behavioural, not a
# constructor-validation duty, so it is not a test obligation.
_VALIDATION_PATTERNS: frozenset[str] = frozenset(
    {"ValueObject", "Entity", "Aggregate"})


class ProjectTestObligations:
    """Projects (ArchitectureSpec, ProblemSpec) -> a TestObligation contract."""

    def project(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> tuple[TestObligation, ...]:
        """Return the deterministic obligation set for ``problem`` on ``arch``."""
        index = self._verb_index(arch)
        outcomes = {normalize(o.verb): o for o in problem.expected_outcomes}
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
            # A verb whose only home is an abstract Gateway port or an
            # Infrastructure adapter is an integration concern (no concrete,
            # unit-testable implementation in the app/domain layers) — it is
            # the developer's integration test, not a unit obligation.
            if module.layer is LayerType.INFRASTRUCTURE:
                continue
            for cls in module.classes:
                if cls.pattern == "Gateway":
                    continue
                for method in cls.methods:
                    name = method.split("(", 1)[0].strip()
                    index.setdefault(normalize(name), (cls.name, name))
        return index

    def _from_criterion(
        self, crit: str, index: dict[str, tuple[str, str]],
        outcomes: dict[str, ExpectedOutcome],
    ) -> TestObligation | None:
        verb = when_verb(crit)
        if verb is None:
            return None
        resolved = index.get(normalize(verb))
        if resolved is None:
            return None
        cls, method = resolved
        outcome = outcomes.get(normalize(verb))
        kind, detail = (
            (AssertionKind(outcome.kind), outcome.value) if outcome is not None
            else then_outcome(crit))
        return TestObligation(cls, method, kind, detail, crit)

    @staticmethod
    def _from_invariants(arch: ArchitectureSpec) -> list[TestObligation]:
        out: list[TestObligation] = []
        for module in arch.modules:
            for cls in module.classes:
                if cls.pattern not in _VALIDATION_PATTERNS:
                    continue
                for inv in cls.invariants:
                    if not is_validation_invariant(inv):
                        continue
                    out.append(TestObligation(
                        cls.name, _CTOR, AssertionKind.RAISES, inv, inv))
        return out
