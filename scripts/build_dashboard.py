#!/usr/bin/env python
"""Standalone entrypoint to rebuild the meta-eval dashboard HTML.

Usage:
    python scripts/build_dashboard.py [<results_root>]

Defaults to ``<repo_parent>/meta-evaluation-results/`` and writes
``dashboard.html`` inside that directory. Safe for cron / CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from squeaky_clean.application.use_cases.html_dashboard_writer import (  # noqa: E402
    HtmlDashboardWriter,
)
from squeaky_clean.application.use_cases.metrics_history_aggregator import (  # noqa: E402
    MetricsHistoryAggregator,
)


def main(argv: list[str]) -> int:
    """Aggregate snapshots and write the dashboard; return 0 on success."""
    default_root = _REPO_ROOT.parent / "meta-evaluation-results"
    root = Path(argv[1]) if len(argv) > 1 else default_root
    snapshots = MetricsHistoryAggregator().aggregate(root)
    target = root / "dashboard.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    HtmlDashboardWriter().write(snapshots, target)
    print(f"dashboard written: {target} ({len(snapshots)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
