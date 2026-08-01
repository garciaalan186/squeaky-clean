"""MaintenanceCommands: resume and dashboard-rebuild command flows."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.metrics_history_aggregator import (
    MetricsHistoryAggregator,
)
from squeaky_clean.application.evaluation.eval.report.html_dashboard_writer import (
    HtmlDashboardWriter,
)
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.resume_dispatch import ResumeDispatch


class MaintenanceCommands:
    """Executes the --resume and --rebuild-dashboard flows."""

    def resume(self, router: ModelRouter, maint: MaintenanceInvocation) -> int:
        """Resume a partially-completed run from its run directory."""
        bundle = ResumeDispatch().resume(router, maint)
        print(f"[squeaky] resume complete: cost="
              f"${bundle.metrics.estimated_cost_usd:.4f}")
        return 0

    def rebuild_dashboard(self) -> int:
        """Rebuild meta-evaluation-results/dashboard.html from run history."""
        framework_root = Path(__file__).resolve().parents[4]
        root = framework_root.parent / "meta-evaluation-results"
        snapshots = MetricsHistoryAggregator(JSONLogger()).aggregate(root)
        target = root / "dashboard.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        HtmlDashboardWriter().write(snapshots, target)
        print(f"[squeaky] dashboard rebuilt: {target} "
              f"({len(snapshots)} runs)")
        return 0
