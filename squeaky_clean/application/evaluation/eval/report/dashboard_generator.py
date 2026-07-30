"""DashboardGenerator: emit a static HTML view of every meta-eval SUMMARY.md."""

from __future__ import annotations

import html
import re
from pathlib import Path

_HEADER = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Squeaky Clean — meta-evaluation history</title>
<style>
  body { font-family: ui-monospace, monospace; max-width: 980px; margin: 2em auto; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 2em; }
  th, td { border: 1px solid #ddd; padding: 4px 8px; font-size: 13px; }
  th { background: #f3f3f3; }
  h2 { margin-top: 2em; }
  pre { background: #f7f7f7; padding: 8px; overflow-x: auto; }
</style></head><body>
<h1>Squeaky Clean — meta-evaluation history</h1>
"""

_FOOTER = "</body></html>\n"


class DashboardGenerator:
    """Walk a meta-evaluation results directory; emit one static HTML page."""

    def generate(self, results_root: Path, output: Path) -> Path:
        """Write `output` containing one section per discovered run."""
        sections: list[str] = []
        for run_dir in sorted(results_root.glob("meta-evaluation_*"), reverse=True):
            summary = run_dir / "SUMMARY.md"
            if not summary.exists():
                continue
            sections.append(self._render_section(run_dir.name, summary.read_text()))
        body = _HEADER + "\n".join(sections) + _FOOTER
        output.write_text(body)
        return output

    def _render_section(self, run_name: str, summary_md: str) -> str:
        rows = self._extract_table_rows(summary_md)
        title = html.escape(run_name)
        rendered_rows = "\n".join(
            "<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>"
            for row in rows
        )
        if rendered_rows:
            table = (
                "<table><thead><tr>"
                + "".join(f"<th>{html.escape(h)}</th>" for h in self._headers(rows))
                + "</tr></thead><tbody>"
                + rendered_rows
                + "</tbody></table>"
            )
        else:
            table = ""
        raw = html.escape(summary_md)
        return f"<h2>{title}</h2>\n{table}\n<details><summary>raw SUMMARY.md</summary><pre>{raw}</pre></details>"

    def _extract_table_rows(self, md: str) -> list[list[str]]:
        rows: list[list[str]] = []
        for line in md.splitlines():
            if not line.startswith("|"):
                continue
            if re.match(r"\|[\s|:-]+\|$", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
        return rows

    def _headers(self, rows: list[list[str]]) -> list[str]:
        return rows[0] if rows else []
