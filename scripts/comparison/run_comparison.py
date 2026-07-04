"""Orchestrate a full comparison run across the three framings.

Usage (from clean-agent-workflow/):
    python -m scripts.comparison.run_comparison \\
        --problem-file examples/event_pipeline/producer_problem.json \\
        --replicates 3 \\
        --max-cost-usd 30.0
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.comparison.baseline_gateway import VanillaOpusGateway
from scripts.comparison.baseline_metrics import BaselineComparisonMetrics
from scripts.comparison.decomposition_metrics import measure as measure_decomposition
from scripts.comparison.problem_spec_to_prose import translate
from scripts.comparison.retry_loop import run as run_retry_loop
from squeaky_clean.domain.interfaces.llm_request import LLMRequest

_DEFAULT_OPUS_MODEL = "claude-opus-4-7"
_TEMPLATES_DIR = Path(__file__).parent / "prompt_templates"


def main() -> int:
    args = _parse_args()
    workflow_root = Path(__file__).parent.parent.parent
    output_root = workflow_root.parent / "meta-evaluation-results"
    run_id = _next_run_id(output_root)
    run_dir = output_root / f"comparison_{run_id:03d}_{_timestamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_methodology_snapshot(run_dir, args)
    problem_path = Path(args.problem_file).resolve()
    spec_dict = json.loads(problem_path.read_text())
    problem_id = spec_dict.get("id", problem_path.stem)
    print(f"[comparison] run_dir={run_dir}")
    print(f"[comparison] problem_id={problem_id}")
    _run_framing_2(run_dir, problem_path, problem_id, args)
    _run_framing_1(run_dir, problem_path, problem_id, args)
    _run_framing_3(run_dir, problem_path, problem_id, args)
    _write_summary(run_dir, problem_id)
    print(f"[comparison] done: {run_dir / 'SUMMARY.md'}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem-file", required=True)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--max-cost-usd", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--opus-model", default=_DEFAULT_OPUS_MODEL)
    parser.add_argument("--skip-squeaky", action="store_true",
                        help="Reuse Squeaky runs from a prior comparison; only run baselines.")
    return parser.parse_args()


def _next_run_id(output_root: Path) -> int:
    output_root.mkdir(parents=True, exist_ok=True)
    existing = sorted(output_root.glob("comparison_*"))
    if not existing:
        return 1
    last = existing[-1].name
    parts = last.split("_")
    try:
        return int(parts[1]) + 1
    except (IndexError, ValueError):
        return len(existing) + 1


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _write_methodology_snapshot(run_dir: Path, args: argparse.Namespace) -> None:
    snapshot = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "problem_file": str(Path(args.problem_file).resolve()),
        "replicates_per_cell": args.replicates,
        "max_retries": args.max_retries,
        "opus_model": args.opus_model,
        "max_cost_usd_cap": args.max_cost_usd,
        "translator_version": "v1",
        "retry_template_version": "v1",
        "framing_2_template_version": "v1",
        "framing_1_brief_version": "v1",
    }
    (run_dir / "methodology.md").write_text(
        "# Comparison run methodology snapshot\n\n```json\n"
        + json.dumps(snapshot, indent=2)
        + "\n```\n"
    )


def _run_framing_2(
    run_dir: Path,
    problem_path: Path,
    problem_id: str,
    args: argparse.Namespace,
) -> None:
    framing_dir = run_dir / "framing_2_info_equivalent"
    framing_dir.mkdir(exist_ok=True)
    translation = translate(problem_path)
    print(f"[framing_2] translator={translation.version}; prompt_chars={len(translation.prompt)}")
    _run_baseline_replicates(
        framing_dir / "vanilla_opus",
        problem_id=problem_id,
        framing="2_info_equivalent",
        user_prompt=translation.prompt,
        translator_version=translation.version,
        prompt_template_version="v1",
        replicates=args.replicates,
        max_retries=args.max_retries,
        opus_model=args.opus_model,
    )


def _run_framing_1(
    run_dir: Path,
    problem_path: Path,
    problem_id: str,
    args: argparse.Namespace,
) -> None:
    framing_dir = run_dir / "framing_1_practical"
    framing_dir.mkdir(exist_ok=True)
    brief = (_TEMPLATES_DIR / "framing_1_practical_brief.md").read_text()
    print(f"[framing_1] brief_chars={len(brief)}")
    _run_baseline_replicates(
        framing_dir / "vanilla_opus",
        problem_id=problem_id,
        framing="1_practical",
        user_prompt=brief,
        translator_version="",
        prompt_template_version="v1",
        replicates=args.replicates,
        max_retries=args.max_retries,
        opus_model=args.opus_model,
    )


def _run_framing_3(
    run_dir: Path,
    problem_path: Path,
    problem_id: str,
    args: argparse.Namespace,
) -> None:
    framing_dir = run_dir / "framing_3_equal_cost"
    framing_dir.mkdir(exist_ok=True)
    translation = translate(problem_path)
    f2_metrics = _read_framing_2_costs(run_dir)
    if not f2_metrics:
        print("[framing_3] WARNING: no framing-2 squeaky cost data; using --max-cost-usd as cap")
        cap = args.max_cost_usd / args.replicates
    else:
        cap = statistics.mean(f2_metrics)
    print(f"[framing_3] per-replicate cost cap=${cap:.4f}")
    _run_baseline_replicates(
        framing_dir / "vanilla_opus",
        problem_id=problem_id,
        framing="3_equal_cost",
        user_prompt=translation.prompt,
        translator_version=translation.version,
        prompt_template_version="v1",
        replicates=args.replicates,
        max_retries=args.max_retries,
        opus_model=args.opus_model,
        cost_cap_per_run=cap,
    )


def _read_framing_2_costs(run_dir: Path) -> list[float]:
    f2 = run_dir / "framing_2_info_equivalent" / "squeaky"
    if not f2.exists():
        return []
    costs: list[float] = []
    for metrics_path in sorted(f2.glob("run_*/metrics.json")):
        try:
            data = json.loads(metrics_path.read_text())
            costs.append(float(data.get("estimated_cost_usd", 0.0)))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return costs


def _run_baseline_replicates(
    cell_dir: Path,
    problem_id: str,
    framing: str,
    user_prompt: str,
    translator_version: str,
    prompt_template_version: str,
    replicates: int,
    max_retries: int,
    opus_model: str,
    cost_cap_per_run: float | None = None,
) -> None:
    cell_dir.mkdir(parents=True, exist_ok=True)
    gateway = VanillaOpusGateway(model=opus_model)
    retry_template = (_TEMPLATES_DIR / "retry_template_v1.md").read_text()
    for replicate_id in range(replicates):
        run_path = cell_dir / f"run_{replicate_id:03d}"
        run_path.mkdir(parents=True, exist_ok=True)
        request = LLMRequest(
            model=opus_model,
            system_prompt="",
            user_prompt=user_prompt,
            temperature=0.0,
            replicate_id=replicate_id,
        )
        print(f"[{framing}] replicate {replicate_id}: starting")
        start = time.monotonic()
        result = run_retry_loop(
            gateway=gateway,
            initial_request=request,
            project_dir=run_path,
            retry_template=retry_template,
            max_retries=max_retries,
        )
        wall_ms = int((time.monotonic() - start) * 1000)
        decomp = measure_decomposition(run_path)
        metrics = BaselineComparisonMetrics(
            framing=framing,
            system="vanilla-opus",
            replicate_id=replicate_id,
            problem_id=problem_id,
            tests_pass=_tests_pass_estimate(result),
            parse_failure=result.final_parse.parse_failure,
            parse_failure_reason=result.final_parse.failure_reason,
            tests_runnable=result.final_coverage.tests_runnable,
            coverage_line_pct=result.final_coverage.line_pct,
            coverage_branch_pct=result.final_coverage.branch_pct,
            estimated_cost_usd=result.total_cost_usd,
            total_wall_clock_ms=wall_ms,
            total_tokens_input=result.total_input_tokens,
            total_tokens_output=result.total_output_tokens,
            retry_count=max(0, len(result.attempts) - 1),
            avg_file_line_count=decomp.avg_file_line_count,
            max_file_line_count=decomp.max_file_line_count,
            classes_per_module=decomp.classes_per_module,
            orphan_files=decomp.orphan_files,
            prompt_template_version=prompt_template_version,
            translator_version=translator_version,
            model_id=opus_model,
        )
        metrics.write(run_path / "metrics.json")
        print(
            f"[{framing}] replicate {replicate_id}: "
            f"cost=${result.total_cost_usd:.3f} "
            f"retries={metrics.retry_count} "
            f"parse_fail={result.final_parse.parse_failure} "
            f"cov_line={result.final_coverage.line_pct:.1f}%"
        )
        if cost_cap_per_run is not None and result.total_cost_usd > cost_cap_per_run:
            print(f"[{framing}] cost cap exceeded; subsequent retries already capped by max_retries")


def _tests_pass_estimate(result) -> float:
    """Coarse pass-rate estimate from coverage runnability + line coverage.

    The neutral test suite isn't yet wired in; this is a placeholder until
    Phase B produces the suite. Returns 0 if tests didn't run; otherwise
    a fraction proportional to line coverage as a coarse correctness proxy.
    """
    if not result.final_coverage.tests_runnable:
        return 0.0
    return min(1.0, result.final_coverage.line_pct / 100.0)


def _write_summary(run_dir: Path, problem_id: str) -> None:
    lines: list[str] = [
        f"# Comparison summary — {problem_id}\n",
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n",
        "",
        "## Per-framing results\n",
    ]
    for framing in ("framing_2_info_equivalent", "framing_1_practical", "framing_3_equal_cost"):
        framing_dir = run_dir / framing
        if not framing_dir.exists():
            continue
        lines.append(f"### {framing}\n")
        lines.append(_framing_table(framing_dir))
        lines.append("")
    (run_dir / "SUMMARY.md").write_text("\n".join(lines))


def _framing_table(framing_dir: Path) -> str:
    rows = []
    rows.append("| System | Replicates | tests_pass μ±σ | cov_line μ±σ | cost μ±σ | wall_ms μ±σ | parse_fail | retries μ |")
    rows.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for system_dir in sorted(framing_dir.iterdir()):
        if not system_dir.is_dir():
            continue
        metrics = _load_cell_metrics(system_dir)
        if not metrics:
            continue
        rows.append(_metrics_row(system_dir.name, metrics))
    return "\n".join(rows)


def _load_cell_metrics(cell_dir: Path) -> list[BaselineComparisonMetrics]:
    out: list[BaselineComparisonMetrics] = []
    for path in sorted(cell_dir.glob("run_*/metrics.json")):
        try:
            out.append(BaselineComparisonMetrics.read(path))
        except (OSError, ValueError):
            continue
    return out


def _metrics_row(system: str, metrics: list[BaselineComparisonMetrics]) -> str:
    n = len(metrics)
    return (
        f"| {system} | {n} | "
        f"{_msd([m.tests_pass for m in metrics])} | "
        f"{_msd([m.coverage_line_pct for m in metrics])} | "
        f"${_msd([m.estimated_cost_usd for m in metrics])} | "
        f"{_msd([m.total_wall_clock_ms for m in metrics], int_=True)} | "
        f"{sum(1 for m in metrics if m.parse_failure)} | "
        f"{sum(m.retry_count for m in metrics) / n:.1f} |"
    )


def _msd(values: list[float], int_: bool = False) -> str:
    if not values:
        return "—"
    mean = sum(values) / len(values)
    if len(values) > 1:
        sd = statistics.stdev(values)
    else:
        sd = 0.0
    if int_:
        return f"{int(mean)}±{int(sd)}"
    return f"{mean:.2f}±{sd:.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
