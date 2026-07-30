"""MicroEvalReportWriter: matrix Markdown + JSON for micro-eval cells (R5.4)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.evaluation.microeval.micro_eval_cell import MicroEvalCell
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text


class MicroEvalReportWriter:
    """Writes micro_eval_report.{md,json} for a batch of cells."""

    def write(self, out_dir: Path, cells: tuple[MicroEvalCell, ...]) -> Path:
        """Persist the pattern x language pass matrix; return the md path."""
        md_path = out_dir / "micro_eval_report.md"
        atomic_write_text(md_path, "\n".join(self._md(cells)))
        atomic_write_text(
            out_dir / "micro_eval_report.json",
            json.dumps([asdict(c) for c in cells], indent=2),
        )
        return md_path

    def _md(self, cells: tuple[MicroEvalCell, ...]) -> list[str]:
        languages = sorted({c.language for c in cells})
        by_key = {(c.pattern, c.language): c for c in cells}
        total_cost = sum(c.cost_usd for c in cells)
        passed = sum(1 for c in cells if c.passed)
        lines = [
            "# Micro-Eval Matrix — compile-verified emission (R5.4)", "",
            f"cells: {len(cells)}  passed: {passed}  "
            f"failed: {len(cells) - passed}  cost: ${total_cost:.4f}", "",
            "| pattern | " + " | ".join(languages) + " |",
            "|---------|" + "|".join(["---"] * len(languages)) + "|",
        ]
        for pattern in sorted({c.pattern for c in cells}):
            row = [self._cell_md(by_key.get((pattern, lang)))
                   for lang in languages]
            lines.append(f"| {pattern} | " + " | ".join(row) + " |")
        failures = [c for c in cells if not c.passed]
        if failures:
            lines.append("")
            lines.append("## Failures")
            for c in failures:
                lines.append(f"- **{c.pattern}/{c.language}** "
                             f"({c.compile_errors} errors): {c.detail[:200]}")
        return lines

    @staticmethod
    def _cell_md(cell: MicroEvalCell | None) -> str:
        if cell is None:
            return "—"
        return "✅" if cell.passed else f"❌ ({cell.compile_errors})"
