"""SweepProblemTable: SUMMARY.md title + per-problem results table."""

from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult


class SweepProblemTable:
    """Renders the header, per-problem markdown table and its footnotes."""

    def render(self, result: SweepResult) -> list[str]:
        """Lines for the top of SUMMARY.md (through the N=1 caveat)."""
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
        return lines
