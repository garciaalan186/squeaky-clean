"""HtmlDashboardWriter: render snapshots to a single self-contained HTML file."""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

from squeaky_clean.application.dtos.run_metrics_snapshot import RunMetricsSnapshot
from squeaky_clean.application.use_cases.dashboard_html_template import (
    DASHBOARD_TEMPLATE,
    EMPTY_TEMPLATE,
)
from squeaky_clean.application.use_cases.dashboard_series_builder import (
    DashboardSeriesBuilder,
    MetricSeries,
)


class HtmlDashboardWriter:
    """Render aggregated meta-eval snapshots into a static dashboard HTML."""

    def write(
        self, snapshots: tuple[RunMetricsSnapshot, ...], output: Path,
    ) -> Path:
        """Write `output`; on empty input write a placeholder; return path."""
        if not snapshots:
            output.write_text(EMPTY_TEMPLATE)
            return output
        series = DashboardSeriesBuilder().build(snapshots)
        body = DASHBOARD_TEMPLATE.format(
            total_runs=len(snapshots),
            date_range=self._date_range(snapshots),
            problem_counts=self._problem_counts(snapshots),
            regressions=self._regressions_block(series),
            charts=self._charts_block(series),
            series_json=json.dumps([self._series_payload(s) for s in series]),
        )
        output.write_text(body)
        return output

    def _date_range(self, snapshots: tuple[RunMetricsSnapshot, ...]) -> str:
        first = html.escape(snapshots[0].timestamp)
        last = html.escape(snapshots[-1].timestamp)
        return f"{first} → {last}"

    def _problem_counts(self, snapshots: tuple[RunMetricsSnapshot, ...]) -> str:
        counts = Counter(s.problem_id or "(unknown)" for s in snapshots)
        return "".join(
            f"<li><code>{html.escape(pid)}</code>: {n}</li>"
            for pid, n in sorted(counts.items())
        )

    def _regressions_block(self, series: tuple[MetricSeries, ...]) -> str:
        flagged = [s for s in series if s.regressions]
        if not flagged:
            return "<p>No regressions flagged in last 10 runs.</p>"
        return "".join(
            f"<div class='reg'><b>{html.escape(s.name)}</b>: runs "
            f"{', '.join(str(r) for r in s.regressions)}</div>"
            for s in flagged
        )

    def _charts_block(self, series: tuple[MetricSeries, ...]) -> str:
        return "".join(
            f"<div class='chart'><h3>{html.escape(s.name)}</h3>"
            f"<canvas id='chart-{html.escape(s.name)}'></canvas></div>"
            for s in series if s.values
        )

    def _series_payload(self, s: MetricSeries) -> dict[str, object]:
        return {
            "name": s.name,
            "labels": list(s.labels),
            "values": list(s.values),
            "rolling_mean": list(s.rolling_mean),
        }
