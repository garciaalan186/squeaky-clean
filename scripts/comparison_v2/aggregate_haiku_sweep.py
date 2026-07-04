"""Aggregate haiku-vs-mixed sweep results across all 5 problems.

Walks meta-evaluation-results/comparison_v2_*/ dirs from today's sweep
(2026-05-13+), groups by (problem, config), and tabulates median +
range for the key metrics.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

OUTPUT_ROOT = Path("/home/alan/git/clean-agents/meta-evaluation-results")
SWEEP_PROBLEMS = ("p0_calculator", "p1_todo_manager", "p3_chat_app", "p5_oauth2_server", "ep_producer")
CUTOFF = "20260513"  # only count runs from today's experiment


def main() -> None:
    cells: dict[tuple[str, str], list[dict]] = {}
    for run_dir in sorted(OUTPUT_ROOT.glob("comparison_v2_*")):
        # Filter by timestamp in dir name
        if CUTOFF not in run_dir.name:
            continue
        cfg_path = run_dir / "config.json"
        if not cfg_path.exists():
            continue
        try:
            cfg = json.loads(cfg_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        slug = cfg.get("problem_slug", "?")
        override = cfg.get("squeaky_model_override", "") or ""
        config = "haiku-all" if "haiku" in override else "mixed-tier"
        sq_dir = run_dir / "squeaky"
        if not sq_dir.exists():
            continue
        for rep_dir in sorted(sq_dir.glob("run_*")):
            metrics_path = rep_dir / "metrics.json"
            eval_path = rep_dir / "eval_report.json"
            if not metrics_path.exists():
                continue
            try:
                m = json.loads(metrics_path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if eval_path.exists():
                try:
                    er = json.loads(eval_path.read_text())
                    for k in ("security_tests_pass", "functional_tests_pass",
                              "max_methods_per_class", "max_file_line_count"):
                        if k in er.get("metrics", {}) and k not in m:
                            m[k] = er["metrics"][k]
                except (OSError, json.JSONDecodeError):
                    pass
            cells.setdefault((slug, config), []).append(m)

    print()
    print("=" * 110)
    print(f"{'Problem':<18} {'Config':<11} {'N':>3} "
          f"{'neutral':>16} {'sec':>13} {'cost':>16} {'wall':>12} {'viol':>5} {'max_m':>6}")
    print("-" * 110)
    for problem in SWEEP_PROBLEMS:
        for config in ("mixed-tier", "haiku-all"):
            ms = cells.get((problem, config), [])
            if not ms:
                print(f"{problem:<18} {config:<11}  -- no data --")
                continue
            neutral = [m.get("tests_pass", 0.0) for m in ms]
            sec = [m["security_tests_pass"] for m in ms if "security_tests_pass" in m]
            cost = [m.get("estimated_cost_usd", 0.0) for m in ms]
            wall = [m.get("total_wall_clock_ms", 0) for m in ms]
            viol = [m.get("architecture_violations", 0) for m in ms]
            mm = [m.get("max_methods_per_class", 0) for m in ms if "max_methods_per_class" in m]
            print(f"{problem:<18} {config:<11} {len(ms):>3} "
                  f"{_med(neutral):>16} {_med(sec):>13} "
                  f"${_med(cost, fmt='.4f'):>15} {_med(wall, fmt='.0f'):>12} "
                  f"{_med(viol, fmt='.0f'):>5} {_med(mm, fmt='.0f'):>6}")
        print()  # blank line between problems
    print("=" * 110)
    print("Format: median (min..max); '-' = no data; viol = architecture_violations;")
    print("        max_m = max_methods_per_class; sec = squeaky internal security_tests_pass")


def _med(values: list, fmt: str = ".2f") -> str:
    if not values:
        return "n/a"
    m = statistics.median(values)
    lo, hi = min(values), max(values)
    if lo == hi:
        return f"{m:{fmt}}"
    return f"{m:{fmt}} ({lo:{fmt}}..{hi:{fmt}})"


if __name__ == "__main__":
    main()
