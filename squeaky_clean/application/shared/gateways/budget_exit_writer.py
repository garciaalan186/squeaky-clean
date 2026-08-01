"""BudgetExitWriter: emits a human-readable BUDGET_EXIT.txt artifact."""

from pathlib import Path


class BudgetExitWriter:
    """Writes ``BUDGET_EXIT.txt`` when a run aborts due to a cost cap.

    Constructed per exit event: ``cap_usd``/``spent_usd`` capture the
    budget state at the moment the run aborted.
    """

    def __init__(self, cap_usd: float | None, spent_usd: float) -> None:
        self._cap_usd: float | None = cap_usd
        self._spent_usd: float = spent_usd

    def write(self, output_dir: Path, stage: str) -> Path:
        """Persist a simple report; return the written path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "BUDGET_EXIT.txt"
        cap_str = ("unlimited" if self._cap_usd is None
                   else f"${self._cap_usd:.4f}")
        body = (
            "Squeaky Clean budget exit\n"
            f"  cap:    {cap_str}\n"
            f"  spent:  ${self._spent_usd:.4f}\n"
            f"  stage:  {stage}\n"
            "  status: aborted gracefully; partial results retained\n"
        )
        path.write_text(body)
        return path
