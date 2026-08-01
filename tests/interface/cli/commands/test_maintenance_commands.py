"""Tests for MaintenanceCommands (resume + dashboard rebuild flows)."""

from pathlib import Path

import pytest

from squeaky_clean.application.evaluation.eval.metrics.metrics_history_aggregator import (
    MetricsHistoryAggregator,
)
from squeaky_clean.application.evaluation.eval.report.html_dashboard_writer import (
    HtmlDashboardWriter,
)
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.commands.maintenance_commands import MaintenanceCommands
from squeaky_clean.interface.cli.invocations.maintenance_invocation import (
    MaintenanceInvocation,
)
from squeaky_clean.interface.cli.resume_dispatch import ResumeDispatch


def test_resume_delegates_to_resume_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[MaintenanceInvocation] = []

    def fake_resume(
        self: ResumeDispatch, router: ModelRouter, maint: MaintenanceInvocation,
    ) -> EvalReportBundle:
        seen.append(maint)
        bundle = type("B", (), {})()
        bundle.metrics = type("M", (), {"estimated_cost_usd": 0.0})()
        return bundle  # type: ignore[return-value]

    monkeypatch.setattr(ResumeDispatch, "resume", fake_resume)
    maint = MaintenanceInvocation(resume_run_dir="run-dir")
    assert MaintenanceCommands().resume(ModelRouter(), maint) == 0
    assert seen == [maint]


def test_rebuild_dashboard_aggregates_and_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written: list[Path] = []

    def fake_aggregate(self: MetricsHistoryAggregator, root: Path) -> list[object]:
        return []

    def fake_write(
        self: HtmlDashboardWriter, snapshots: object, target: Path,
    ) -> None:
        written.append(target)

    monkeypatch.setattr(MetricsHistoryAggregator, "aggregate", fake_aggregate)
    monkeypatch.setattr(HtmlDashboardWriter, "write", fake_write)
    assert MaintenanceCommands().rebuild_dashboard() == 0
    assert written and written[0].name == "dashboard.html"
