"""BudgetExitWriter: emits a human-readable BUDGET_EXIT.txt artifact."""

from pathlib import Path


class BudgetExitWriter:
    """Writes ``BUDGET_EXIT.txt`` when a run aborts due to a cost cap."""

    def write(
        self, output_dir: Path, cap_usd: float | None, spent_usd: float,
        stage: str,
    ) -> Path:
        """Persist a simple report; return the written path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "BUDGET_EXIT.txt"
        cap_str = "unlimited" if cap_usd is None else f"${cap_usd:.4f}"
        body = (
            "Squeaky Clean budget exit\n"
            f"  cap:    {cap_str}\n"
            f"  spent:  ${spent_usd:.4f}\n"
            f"  stage:  {stage}\n"
            "  status: aborted gracefully; partial results retained\n"
        )
        path.write_text(body)
        return path
