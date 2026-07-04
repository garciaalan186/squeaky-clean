"""Comparison v2 orchestrator.

Runs N replicates of Squeaky and Vanilla Opus on a single problem, applies
the per-problem neutral test suite to BOTH symmetrically, and writes
per-replicate metrics + a summary.

For the full sweep across multiple problems / framings, this script is
called once per (problem, framing) cell.

Usage:
    python -m scripts.comparison_v2.run_v2 \\
        --problem-slug p0_calculator \\
        --replicates 3 \\
        --framing info_equivalent
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.comparison.baseline_gateway import VanillaOpusGateway
from scripts.comparison.decomposition_metrics import measure as measure_decomposition
from scripts.comparison.problem_spec_to_prose import translate
from scripts.comparison.retry_loop import run as run_retry_loop
from scripts.comparison_v2.neutral_suite_runner import apply_and_score
from squeaky_clean.domain.interfaces.llm_request import LLMRequest

WORKFLOW_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = WORKFLOW_ROOT / "eval" / "comparison_v2"
OUTPUT_ROOT = WORKFLOW_ROOT.parent / "meta-evaluation-results"
TEMPLATES_DIR = WORKFLOW_ROOT / "scripts" / "comparison" / "prompt_templates"
DEFAULT_OPUS_MODEL = "claude-opus-4-7"


def main() -> int:
    args = _parse_args()
    problem_slug = args.problem_slug
    asset_dir = ASSETS_ROOT / problem_slug
    if not asset_dir.is_dir():
        print(f"ERROR: no v2 assets at {asset_dir}", file=sys.stderr)
        return 1
    problem_path = asset_dir / "problem.json"
    spec_dict = json.loads(problem_path.read_text())
    problem_id = spec_dict["id"]

    run_dir = _allocate_run_dir(problem_slug, args.framing)
    print(f"[v2] run_dir={run_dir}")
    print(f"[v2] problem={problem_id} ({problem_slug}) replicates={args.replicates}")

    _write_methodology_snapshot(run_dir, args, problem_path)

    if not args.skip_opus:
        _run_opus_cell(run_dir, problem_path, problem_slug, problem_id, args)
    if not args.skip_squeaky:
        _run_squeaky_cell(run_dir, problem_id, problem_slug, args)

    _write_summary(run_dir, problem_id, problem_slug)
    print(f"[v2] done: {run_dir / 'SUMMARY.md'}")
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--problem-slug", required=True,
                   help="Slug under eval/comparison_v2/ (e.g. p0_calculator)")
    p.add_argument("--replicates", type=int, default=3)
    p.add_argument("--framing", default="info_equivalent",
                   choices=["info_equivalent", "practical"])
    p.add_argument("--max-retries", type=int, default=2)
    p.add_argument("--opus-model", default=DEFAULT_OPUS_MODEL)
    p.add_argument("--skip-opus", action="store_true")
    p.add_argument("--skip-squeaky", action="store_true")
    p.add_argument("--squeaky-model-override", default=None,
                   help="If set, pass --model-override to the Squeaky CLI "
                        "(e.g. claude-haiku-4-5-20251001 for haiku-all-tiers).")
    return p.parse_args()


def _allocate_run_dir(problem_slug: str, framing: str) -> Path:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    existing = sorted(OUTPUT_ROOT.glob("comparison_v2_*"))
    next_id = len(existing) + 1
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = OUTPUT_ROOT / f"comparison_v2_{next_id:03d}_{ts}_{problem_slug}_{framing}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_methodology_snapshot(run_dir: Path, args: argparse.Namespace,
                                 problem_path: Path) -> None:
    snapshot = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "problem_path": str(problem_path),
        "problem_slug": args.problem_slug,
        "framing": args.framing,
        "replicates_per_cell": args.replicates,
        "max_retries": args.max_retries,
        "opus_model": args.opus_model,
        "neutral_suite_root": str(ASSETS_ROOT / args.problem_slug / "neutral_test"),
        "squeaky_model_override": args.squeaky_model_override or "",
    }
    (run_dir / "config.json").write_text(json.dumps(snapshot, indent=2))


def _run_opus_cell(run_dir: Path, problem_path: Path, problem_slug: str,
                   problem_id: str, args: argparse.Namespace) -> None:
    cell_dir = run_dir / "vanilla_opus"
    cell_dir.mkdir(parents=True, exist_ok=True)
    if args.framing == "info_equivalent":
        translation = translate(problem_path)
        user_prompt = translation.prompt
        translator_version = translation.version
    else:
        brief = (TEMPLATES_DIR / "framing_1_practical_brief.md").read_text()
        user_prompt = brief
        translator_version = ""
    gateway = VanillaOpusGateway(model=args.opus_model)
    retry_template = (TEMPLATES_DIR / "retry_template_v1.md").read_text()
    for replicate_id in range(args.replicates):
        run_path = cell_dir / f"run_{replicate_id:03d}"
        run_path.mkdir(parents=True, exist_ok=True)
        request = LLMRequest(
            model=args.opus_model, system_prompt="", user_prompt=user_prompt,
            temperature=0.0, replicate_id=replicate_id,
        )
        print(f"[opus] replicate {replicate_id}: starting")
        start = time.monotonic()
        try:
            result = run_retry_loop(
                gateway=gateway, initial_request=request, project_dir=run_path,
                retry_template=retry_template, max_retries=args.max_retries,
            )
        except Exception as exc:
            print(f"[opus] replicate {replicate_id}: FAILED: {exc}")
            (run_path / "error.txt").write_text(str(exc))
            continue
        wall_ms = int((time.monotonic() - start) * 1000)
        decomp = measure_decomposition(run_path)
        neutral = apply_and_score(problem_slug, run_path)
        metrics = {
            "system": "vanilla_opus",
            "framing": args.framing,
            "problem_id": problem_id,
            "problem_slug": problem_slug,
            "replicate_id": replicate_id,
            "model_id": args.opus_model,
            "translator_version": translator_version,
            "estimated_cost_usd": result.total_cost_usd,
            "total_wall_clock_ms": wall_ms,
            "total_tokens_input": result.total_input_tokens,
            "total_tokens_output": result.total_output_tokens,
            "retry_count": max(0, len(result.attempts) - 1),
            "parse_failure": result.final_parse.parse_failure,
            "avg_file_line_count": decomp.avg_file_line_count,
            "max_file_line_count": decomp.max_file_line_count,
            "classes_per_module": decomp.classes_per_module,
            "orphan_files": decomp.orphan_files,
            "neutral": neutral.to_dict(),
            "tests_pass": neutral.pass_rate,
        }
        (run_path / "metrics.json").write_text(json.dumps(metrics, indent=2))
        print(f"[opus] replicate {replicate_id}: cost=${result.total_cost_usd:.3f} "
              f"wall={wall_ms}ms tests_pass={neutral.pass_rate:.2f} "
              f"({neutral.tests_passed}/{neutral.tests_collected})")


def _run_squeaky_cell(run_dir: Path, problem_id: str, problem_slug: str,
                      args: argparse.Namespace) -> None:
    cell_dir = run_dir / "squeaky"
    cell_dir.mkdir(parents=True, exist_ok=True)
    # Squeaky generates one meta-evaluation dir under meta-evaluation-results/;
    # each replicate gets its own subdir there. We invoke once with --replicates N.
    # Built-in problems (P0-P5) use --problem PROBLEM_ID; external problems
    # (EP-PROD etc.) use --problem-file with the comparison_v2 problem.json.
    asset_problem = ASSETS_ROOT / args.problem_slug / "problem.json"
    if problem_id and len(problem_id) <= 4 and problem_id[0] == "P" and problem_id[1:].isdigit():
        cmd = [
            sys.executable, "-m", "squeaky_clean.interface.cli",
            "--problem", problem_id,
            "--replicates", str(args.replicates),
        ]
    else:
        cmd = [
            sys.executable, "-m", "squeaky_clean.interface.cli",
            "--problem-file", str(asset_problem),
            "--replicates", str(args.replicates),
        ]
    if args.squeaky_model_override:
        cmd += ["--model-override", args.squeaky_model_override]
    print(f"[squeaky] launching: {' '.join(cmd)}")
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=WORKFLOW_ROOT, capture_output=True, text=True,
                          timeout=60 * 30, check=False)
    wall_ms_total = int((time.monotonic() - start) * 1000)
    (cell_dir / "stdout.txt").write_text(proc.stdout)
    (cell_dir / "stderr.txt").write_text(proc.stderr)
    if proc.returncode != 0:
        print(f"[squeaky] returncode={proc.returncode}; check stderr.txt")
    # Parse squeaky's structured stdout for THIS invocation's run_dir.
    # Avoids the race condition where `sq_runs[-1]` picked the wrong dir
    # under parallel sweep invocations (2026-05-13 finding).
    latest: Path | None = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("kind") == "sweep_started" and "run_dir" in evt:
            latest = Path(evt["run_dir"])
            break
    if latest is None:
        # Fallback to glob-based discovery (single-invocation case)
        sq_runs = sorted(OUTPUT_ROOT.glob("meta-evaluation_*"))
        if not sq_runs:
            print("[squeaky] no run dir produced")
            return
        latest = sq_runs[-1]
    # Find replicate dirs matching this problem
    replicate_dirs = sorted(latest.glob(f"problem-set-*-{problem_slug.replace('_', '-')}*"))
    if not replicate_dirs:
        # Fallback: any subdir containing the problem slug
        replicate_dirs = [d for d in latest.iterdir() if d.is_dir() and problem_slug.split("_")[1] in d.name]
    print(f"[squeaky] found {len(replicate_dirs)} replicate dirs in {latest}")
    for replicate_id, src_dir in enumerate(replicate_dirs):
        dst = cell_dir / f"run_{replicate_id:03d}"
        dst.mkdir(parents=True, exist_ok=True)
        for child in src_dir.iterdir():
            if child.name in ("__pycache__", ".pytest_cache"):
                continue
            target = dst / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if child.is_dir():
                shutil.copytree(child, target)
            else:
                shutil.copy2(child, target)
        decomp = measure_decomposition(dst)
        neutral = apply_and_score(problem_slug, dst)
        # Read squeaky's own eval_report if present
        report_path = dst / "eval_report.json"
        sq_metrics: dict = {}
        if report_path.exists():
            try:
                sq_metrics = json.loads(report_path.read_text()).get("metrics", {})
            except (OSError, json.JSONDecodeError):
                pass
        metrics = {
            "system": "squeaky",
            "framing": args.framing,
            "problem_id": problem_id,
            "problem_slug": problem_slug,
            "replicate_id": replicate_id,
            "model_id": "claude-sonnet-4-6+claude-haiku-4-5",
            "estimated_cost_usd": float(sq_metrics.get("estimated_cost_usd", 0.0)),
            "total_wall_clock_ms": int(sq_metrics.get("total_wall_clock_ms", 0)),
            "total_tokens_input": int(sq_metrics.get("total_tokens_input", 0)),
            "total_tokens_output": int(sq_metrics.get("total_tokens_output", 0)),
            "retry_count": int(sq_metrics.get("agent_retries", 0)),
            "architecture_violations": int(sq_metrics.get("architecture_violations", 0)),
            "compile_errors": int(sq_metrics.get("compile_errors", 0)),
            "avg_file_line_count": decomp.avg_file_line_count,
            "max_file_line_count": decomp.max_file_line_count,
            "classes_per_module": decomp.classes_per_module,
            "orphan_files": decomp.orphan_files,
            "neutral": neutral.to_dict(),
            "tests_pass": neutral.pass_rate,
        }
        (dst / "metrics.json").write_text(json.dumps(metrics, indent=2))
        print(f"[squeaky] replicate {replicate_id}: tests_pass={neutral.pass_rate:.2f} "
              f"({neutral.tests_passed}/{neutral.tests_collected}) "
              f"cost=${metrics['estimated_cost_usd']:.3f}")


def _write_summary(run_dir: Path, problem_id: str, problem_slug: str) -> None:
    lines: list[str] = [
        f"# Comparison v2 — {problem_id} ({problem_slug})",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Per-system results (neutral suite scoring)",
        "",
        "| System | N | tests_pass μ±σ | cost μ±σ | wall_ms μ±σ | retries μ |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for system in ("vanilla_opus", "squeaky"):
        cell = run_dir / system
        metrics = _load_cell(cell)
        if not metrics:
            continue
        lines.append(_metrics_row(system, metrics))
    (run_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def _load_cell(cell_dir: Path) -> list[dict]:
    if not cell_dir.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(cell_dir.glob("run_*/metrics.json")):
        try:
            out.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def _metrics_row(system: str, metrics: list[dict]) -> str:
    n = len(metrics)
    tp = [m.get("tests_pass", 0.0) for m in metrics]
    cost = [m.get("estimated_cost_usd", 0.0) for m in metrics]
    wall = [m.get("total_wall_clock_ms", 0) for m in metrics]
    rt = [m.get("retry_count", 0) for m in metrics]
    return (
        f"| {system} | {n} | {_msd(tp)} | ${_msd(cost)} | {_msd(wall, int_=True)} | "
        f"{sum(rt) / n:.1f} |"
    )


def _msd(values: list[float], int_: bool = False) -> str:
    if not values:
        return "—"
    mean = sum(values) / len(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return f"{int(mean)}±{int(sd)}" if int_ else f"{mean:.2f}±{sd:.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
