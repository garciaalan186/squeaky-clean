"""Tests for the Triage phase: InteractiveTriage + RefactorPlanSerializer."""

import json

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport
from squeaky_clean.application.use_cases.recovery.interactive_triage import (
    InteractiveTriage,
)
from squeaky_clean.application.use_cases.recovery.refactor_plan_serializer import (
    RefactorPlanSerializer,
)

_COUPLING = ArchitecturalViolation("framework-coupling", "app.Page", "d", "s")
_GRANULARITY = ArchitecturalViolation("granularity", "God", "d", "s")
_REPORT = ViolationReport((_COUPLING, _GRANULARITY))


class _Recorder:
    """A testable ``ask``: records prompts, ignores one named category."""

    def __init__(self, ignore_category: str | None = None) -> None:
        self.seen: list[tuple[str, int]] = []
        self._ignore: str | None = ignore_category

    def __call__(self, category: str, count: int) -> bool:
        self.seen.append((category, count))
        return category != self._ignore


def test_every_category_addressed_by_default() -> None:
    plan = InteractiveTriage().run(_REPORT, _Recorder())
    assert set(plan.fix) == {"framework-coupling:app.Page", "granularity:God"}
    assert plan.ignore == ()


def test_a_category_can_be_opted_out() -> None:
    plan = InteractiveTriage().run(_REPORT, _Recorder("granularity"))
    assert plan.fix == ("framework-coupling:app.Page",)
    assert plan.ignore == ("granularity:God",)


def test_ask_is_prompted_once_per_category_with_count() -> None:
    recorder = _Recorder()
    InteractiveTriage().run(_REPORT, recorder)
    assert set(recorder.seen) == {("framework-coupling", 1), ("granularity", 1)}


def test_plan_serializes_to_stable_json() -> None:
    plan = InteractiveTriage().run(_REPORT, _Recorder("framework-coupling"))
    data = json.loads(RefactorPlanSerializer().serialize(plan))
    assert data["fix"] == ["granularity:God"]
    assert data["ignore"] == ["framework-coupling:app.Page"]
