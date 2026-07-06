"""RunEvalSummaryWriter: renders SUMMARY.md from a per-problem eval bundle."""

from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.use_cases.cache_summary_renderer import CacheSummaryRenderer


class RunEvalSummaryWriter:
    """Writes a human-readable SUMMARY.md for one meta-eval run."""

    def __init__(self) -> None:
        self._cache_renderer: CacheSummaryRenderer = CacheSummaryRenderer()

    def write(self, path: Path, bundle: EvalReportBundle) -> None:
        """Render ``bundle`` to a Markdown summary at ``path``."""
        m = bundle.metrics
        lines: list[str] = []
        lines.append(f"# Meta-Evaluation Summary — {path.parent.name}")
        lines.append("")
        lines.append("## Model Routing")
        lines.append("- ARCHITECT  -> claude-sonnet-4-6 (Phase 5 cost override)")
        lines.append("- MANAGER    -> claude-sonnet-4-6")
        lines.append("- ICP        -> claude-haiku-4-5-20251001")
        lines.append("")
        lines.append("## Per-Problem Results")
        lines.append("")
        lines.append("| id | pass rate | violations | cost USD | duration ms |")
        lines.append("|----|-----------|------------|----------|-------------|")
        pass_rate = (f"{m.tests_pass:.2f}" if m.test_status == "ok"
                     else f"— ({m.test_status})")
        lines.append(
            f"| {bundle.problem.id} | {pass_rate} "
            f"| {m.architecture_violations} "
            f"| {m.estimated_cost_usd:.4f} "
            f"| {m.total_wall_clock_ms} |"
        )
        lines.append("")
        lines.append("## Aggregate Totals")
        lines.append("- problems run: 1")
        lines.append(f"- total cost USD: {m.estimated_cost_usd:.4f}")
        lines.append(f"- total duration ms: {m.total_wall_clock_ms}")
        lines.append("")
        lines.extend(self._cache_renderer.render(m))
        self._render_acs(lines, bundle)
        self._honest_assessment(lines, bundle)
        path.write_text("\n".join(lines))

    @staticmethod
    def _render_acs(lines: list[str], bundle: EvalReportBundle) -> None:
        """Render Architectural Complexity Score section."""
        m = bundle.metrics
        if m.acs_composite <= 0:
            return
        lines.append("## Architectural Complexity (ACS)")
        lines.append("")
        lines.append("| Dimension | Value | Weight | Contribution |")
        lines.append("|---|---:|---:|---:|")
        lines.append(f"| Structural | {m.acs_structural} | 0.5 | "
                     f"{m.acs_structural * 0.5:.2f} |")
        lines.append(f"| Codegen    | {m.acs_codegen} | 0.3 | "
                     f"{m.acs_codegen * 0.3:.2f} |")
        lines.append(f"| Constraint | {m.acs_constraint} | 0.2 | "
                     f"{m.acs_constraint * 0.2:.2f} |")
        lines.append(f"| **Composite (ACS)** |  |  | **{m.acs_composite}** |")
        lines.append(f"| **Normalized (P0=1.0)** |  |  | "
                     f"**{m.acs_normalized}** |")
        lines.append("")
        lines.append(f"- Cost per ACS-unit: ${m.acs_cost_per_unit:.4f}")
        lines.append(f"- ACS velocity (units/sec): {m.acs_velocity}")
        lines.append("")

    def _honest_assessment(
        self, lines: list[str], bundle: EvalReportBundle,
    ) -> None:
        pr = bundle.test_run_result
        m = bundle.metrics
        total = pr.passed + pr.failed + pr.errors
        lines.append("## Honest Assessment")
        lines.append(
            f"- tests: {pr.passed} passed, {pr.failed} failed, "
            f"{pr.errors} errors (of {total})"
        )
        lines.append(f"- test status: {m.test_status}")
        lines.append(
            f"- functional pass: {m.functional_tests_pass:.2f} "
            f"({m.functional_test_count} tests) | "
            f"security pass: {m.security_tests_pass:.2f} "
            f"({m.security_test_count} tests)"
        )
        lines.append(
            f"- architecture violations: {len(bundle.validation.violations)}"
        )
        lines.append(f"- files scanned: {bundle.validation.files_scanned}")
        lines.append("")
        if bundle.validation.violations:
            lines.append("## Architectural Violations")
            for v in bundle.validation.violations:
                lines.append(f"- [{v.rule_name}] {v.file_path}: {v.message}")
            lines.append("")
        if pr.failed > 0 or pr.errors > 0:
            lines.append("## Test Failure Excerpt")
            lines.append("```")
            for raw in pr.raw_output.splitlines()[:10]:
                lines.append(raw)
            lines.append("```")
            lines.append("")
