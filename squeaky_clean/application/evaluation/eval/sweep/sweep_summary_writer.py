"""SweepSummaryWriter: cross-problem SUMMARY.md for one parallel sweep run."""

import json
from dataclasses import asdict

from squeaky_clean.application.evaluation.eval.metrics.cache_summary_renderer import (
    CacheSummaryRenderer,
)
from squeaky_clean.application.evaluation.eval.metrics.unmeasured_nulls import (
    null_unmeasured,
)
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.tier_cache_stats import TierCacheStats


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
            # Unmeasured is n/a, never 0.00 (R5.3) — a reader must be able to
            # tell "insecure" from "security tests not enabled".
            security = ("n/a" if m.test_outcome.security_test_count == 0
                        else f"{m.security_tests_pass:.2f}")
            violations = (f"{m.architecture_violations} ⚠"
                          if m.architecture_violations > 0
                          else "0")
            lines.append(
                f"| {b.problem.id}{tag} | {m.tests_pass:.2f} "
                f"| {m.functional_tests_pass:.2f} "
                f"| {security} "
                f"| {violations} | {m.reliability.classes_fixed} "
                f"| {m.estimated_cost_usd:.4f} "
                f"| {m.total_wall_clock_ms} |"
            )
        lines.append("")
        lines.append(
            "> tests/functional = functional acceptance criteria only; "
            "security = generated security tests (n/a = not measured — "
            "enable with `--security-tests`)."
        )
        lines.append("")
        lines.append(
            "> single sample per problem (N=1) — exploratory; fix/regression "
            "claims require N>=3 replicates (`--replicates 3`)."
        )
        lines.extend(self._regression_gate(result))
        lines.extend(self._totals(result))
        lines.extend(self._cache_renderer.render(self._aggregate_metrics(result)))
        lines.extend(self._errors(result))
        atomic_write_text(result.run_dir / "SUMMARY.md", "\n".join(lines))
        self._write_metrics(result)

    def _aggregate_metrics(self, result: SweepResult) -> EvalMetrics:
        by_tier: dict[str, TierCacheStats] = {}
        create, read, savings = 0, 0, 0.0
        for b in result.bundles:
            m = b.metrics
            for tier, stats in m.cache_by_tier.items():
                prev = by_tier.get(tier, TierCacheStats())
                by_tier[tier] = prev.combined(stats)
            create += m.cache_creation_input_tokens
            read += m.cache_read_input_tokens
            savings += m.cache_savings_usd
        return EvalMetrics(
            cache_by_tier=by_tier,
            cache_creation_input_tokens=create,
            cache_read_input_tokens=read,
            cache_savings_usd=savings,
        )

    def _totals(self, result: SweepResult) -> list[str]:
        n = len(result.bundles)
        passed = sum(1 for b in result.bundles if b.metrics.tests_pass >= 1.0)
        fully_passed = sum(
            1 for b in result.bundles if b.metrics.functional_tests_pass >= 1.0
        )
        fixed = sum(b.metrics.reliability.classes_fixed for b in result.bundles)
        return [
            "", "## Aggregate Totals",
            f"- problems run: {n}",
            f"- problems at 100% (overall): {passed}/{n}",
            f"- problems at 100% (functional): {fully_passed}/{n}",
            f"- classes fixed by Sonnet fixer: {fixed}",
            f"- total cost USD: {result.total_cost_usd:.4f}",
            f"- total wall-clock ms: {result.total_duration_ms}",
        ]

    def _regression_gate(self, result: SweepResult) -> list[str]:
        if not result.regression_verdicts:
            return []
        out = ["", "## Regression Gate (vs routing-stamped goldens)"]
        out.extend(f"- {v}" for v in result.regression_verdicts)
        return out

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
            "schema_version": 2,
            "run_dir": str(result.run_dir),
            "total_cost_usd": result.total_cost_usd,
            "total_duration_ms": result.total_duration_ms,
            "problems": [
                {"problem_id": b.problem.id,
                 "metrics": null_unmeasured(asdict(b.metrics))}
                for b in result.bundles
            ],
        }
        atomic_write_text(
            result.run_dir / "metrics.json",
            json.dumps(payload, indent=2, default=str),
        )
