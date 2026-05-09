"""SweepSummaryWriter: cross-problem SUMMARY.md for one parallel sweep run."""

import json
from dataclasses import asdict

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.sweep_result import SweepResult
from squeaky_clean.application.use_cases.cache_summary_renderer import CacheSummaryRenderer


class SweepSummaryWriter:
    """Renders the run-dir SUMMARY.md + metrics.json for a sweep."""

    def __init__(self) -> None:
        self._cache_renderer: CacheSummaryRenderer = CacheSummaryRenderer()

    def write(self, result: SweepResult) -> None:
        """Write SUMMARY.md and aggregate metrics.json into ``result.run_dir``."""
        lines: list[str] = [
            f"# Meta-Evaluation Sweep — {result.run_dir.name}", "",
            "## Per-Problem Results", "",
            "| id | tests | functional | security | violations "
            "| classes_fixed | cost USD | duration ms |",
            "|----|-------|-----------|----------|------------"
            "|---------------|----------|-------------|",
        ]
        for b in result.bundles:
            m = b.metrics
            tag = " ⚠️" if b.error else ""
            lines.append(
                f"| {b.problem.id}{tag} | {m.tests_pass:.2f} "
                f"| {m.functional_tests_pass:.2f} "
                f"| {m.security_tests_pass:.2f} "
                f"| {m.architecture_violations} | {m.classes_fixed} "
                f"| {m.estimated_cost_usd:.4f} "
                f"| {m.total_wall_clock_ms} |"
            )
        lines.extend(self._totals(result))
        lines.extend(self._cache_renderer.render(self._aggregate_metrics(result)))
        lines.extend(self._errors(result))
        (result.run_dir / "SUMMARY.md").write_text("\n".join(lines))
        self._write_metrics(result)

    def _aggregate_metrics(self, result: SweepResult) -> EvalMetrics:
        agg = EvalMetrics.empty()
        for b in result.bundles:
            m = b.metrics
            for tier in ("architect", "manager", "icp", "fixer"):
                for kind in ("create", "read"):
                    f = f"cache_{kind}_{tier}_tokens"
                    setattr(agg, f, getattr(agg, f) + getattr(m, f))
                f = f"cache_savings_{tier}_usd"
                setattr(agg, f, getattr(agg, f) + getattr(m, f))
            agg.cache_creation_input_tokens += m.cache_creation_input_tokens
            agg.cache_read_input_tokens += m.cache_read_input_tokens
            agg.cache_savings_usd += m.cache_savings_usd
        for tier in ("architect", "manager", "icp", "fixer"):
            c = int(getattr(agg, f"cache_create_{tier}_tokens"))
            r = int(getattr(agg, f"cache_read_{tier}_tokens"))
            ratio = (r / (c + r)) if (c + r) > 0 else 0.0
            setattr(agg, f"cache_hit_ratio_{tier}", ratio)
        return agg

    def _totals(self, result: SweepResult) -> list[str]:
        n = len(result.bundles)
        passed = sum(1 for b in result.bundles if b.metrics.tests_pass >= 1.0)
        fully_passed = sum(
            1 for b in result.bundles if b.metrics.functional_tests_pass >= 1.0
        )
        fixed = sum(b.metrics.classes_fixed for b in result.bundles)
        return [
            "", "## Aggregate Totals",
            f"- problems run: {n}",
            f"- problems at 100% (overall): {passed}/{n}",
            f"- problems at 100% (functional): {fully_passed}/{n}",
            f"- classes fixed by Sonnet fixer: {fixed}",
            f"- total cost USD: {result.total_cost_usd:.4f}",
            f"- total wall-clock ms: {result.total_duration_ms}",
        ]

    def _errors(self, result: SweepResult) -> list[str]:
        failed = [b for b in result.bundles if b.error]
        if not failed:
            return []
        out: list[str] = ["", "## Failed Problems"]
        for b in failed:
            out.append(f"- **{b.problem.id}**: {b.error}")
        return out

    def _write_metrics(self, result: SweepResult) -> None:
        payload = {
            "run_dir": str(result.run_dir),
            "total_cost_usd": result.total_cost_usd,
            "total_duration_ms": result.total_duration_ms,
            "problems": [
                {"problem_id": b.problem.id, "metrics": asdict(b.metrics)}
                for b in result.bundles
            ],
        }
        (result.run_dir / "metrics.json").write_text(
            json.dumps(payload, indent=2, default=str)
        )
