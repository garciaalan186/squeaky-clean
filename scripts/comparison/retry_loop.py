"""Retry-equipped baseline runner.

Runs the baseline gateway against an initial prompt; if the materialized
project fails tests, parse, or compile, regenerates with a retry prompt
that includes the failure log and the previous code. Up to N retries
(default 2 to match Squeaky's --max-fixer-passes). Records every
attempt's response on a retry log so the methodology is auditable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from scripts.comparison.baseline_gateway import BaselineLLMGateway
from scripts.comparison.coverage_collector import CoverageResult, collect
from scripts.comparison.file_block_parser import ParseResult, parse_baseline_output
from scripts.comparison.project_materializer import materialize
from squeaky_clean.domain.interfaces.llm_request import LLMRequest


@dataclass(frozen=True)
class Attempt:
    """One pass through the baseline pipeline."""

    attempt_number: int
    parse_failure: bool
    parse_failure_reason: str
    file_count: int
    coverage_line_pct: float
    coverage_branch_pct: float
    tests_runnable: bool
    cost_usd: float
    duration_ms: int
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class RetryLoopResult:
    """Final outcome of a retry-equipped baseline run."""

    project_dir: Path
    attempts: tuple[Attempt, ...]
    final_parse: ParseResult
    final_coverage: CoverageResult
    total_cost_usd: float
    total_duration_ms: int
    total_input_tokens: int
    total_output_tokens: int


def run(
    gateway: BaselineLLMGateway,
    initial_request: LLMRequest,
    project_dir: Path,
    retry_template: str,
    max_retries: int = 2,
) -> RetryLoopResult:
    """Run the baseline with retry-on-failure until success or max_retries."""
    attempts: list[Attempt] = []
    request = initial_request
    parse: ParseResult | None = None
    coverage: CoverageResult | None = None
    total_cost = 0.0
    total_duration = 0
    total_in = 0
    total_out = 0
    for attempt_idx in range(max_retries + 1):
        response = gateway.complete(request)
        total_cost += response.cost_usd
        total_duration += response.duration_ms
        total_in += response.input_tokens
        total_out += response.output_tokens
        parse = parse_baseline_output(response.content)
        attempt_dir = project_dir / f"attempt_{attempt_idx}"
        if not parse.parse_failure:
            mat = materialize(parse, attempt_dir)
            (project_dir / "src").mkdir(exist_ok=True)
            _copy_to_main(mat.project_dir, project_dir)
            coverage = collect(project_dir)
        else:
            coverage = CoverageResult(line_pct=0.0, branch_pct=0.0, tests_runnable=False)
        attempts.append(Attempt(
            attempt_number=attempt_idx,
            parse_failure=parse.parse_failure,
            parse_failure_reason=parse.failure_reason,
            file_count=len(parse.files),
            coverage_line_pct=coverage.line_pct,
            coverage_branch_pct=coverage.branch_pct,
            tests_runnable=coverage.tests_runnable,
            cost_usd=response.cost_usd,
            duration_ms=response.duration_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        ))
        if _is_success(parse, coverage):
            break
        if attempt_idx == max_retries:
            break
        request = _retry_request(request, response.content, parse, coverage, retry_template)
    _write_retry_log(project_dir, attempts)
    assert parse is not None and coverage is not None
    return RetryLoopResult(
        project_dir=project_dir,
        attempts=tuple(attempts),
        final_parse=parse,
        final_coverage=coverage,
        total_cost_usd=total_cost,
        total_duration_ms=total_duration,
        total_input_tokens=total_in,
        total_output_tokens=total_out,
    )


def _is_success(parse: ParseResult, coverage: CoverageResult) -> bool:
    return (
        not parse.parse_failure
        and coverage.tests_runnable
        and coverage.line_pct > 0.0
    )


def _retry_request(
    previous: LLMRequest,
    previous_response_content: str,
    parse: ParseResult,
    coverage: CoverageResult,
    template: str,
) -> LLMRequest:
    failure_log = _build_failure_log(parse, coverage)
    user_prompt = template.format(
        failure_log=failure_log,
        previous_code=previous_response_content,
    )
    return LLMRequest(
        model=previous.model,
        system_prompt=previous.system_prompt,
        user_prompt=user_prompt,
        temperature=previous.temperature,
    )


def _build_failure_log(parse: ParseResult, coverage: CoverageResult) -> str:
    lines: list[str] = []
    if parse.parse_failure:
        lines.append(f"PARSE FAILURE: {parse.failure_reason}")
    if not coverage.tests_runnable:
        lines.append("Tests did not run.")
    if coverage.failure_log:
        lines.append("PYTEST OUTPUT:")
        lines.append(coverage.failure_log[-3000:])
    return "\n".join(lines) if lines else "(no specific failure captured)"


def _copy_to_main(attempt_dir: Path, project_dir: Path) -> None:
    import shutil
    for child in attempt_dir.iterdir():
        target = project_dir / child.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def _write_retry_log(project_dir: Path, attempts: list[Attempt]) -> None:
    log_path = project_dir / "retry_log.json"
    log_path.write_text(json.dumps(
        [_attempt_dict(a) for a in attempts], indent=2,
    ))


def _attempt_dict(a: Attempt) -> dict:
    return {
        "attempt_number": a.attempt_number,
        "parse_failure": a.parse_failure,
        "parse_failure_reason": a.parse_failure_reason,
        "file_count": a.file_count,
        "coverage_line_pct": a.coverage_line_pct,
        "coverage_branch_pct": a.coverage_branch_pct,
        "tests_runnable": a.tests_runnable,
        "cost_usd": a.cost_usd,
        "duration_ms": a.duration_ms,
        "input_tokens": a.input_tokens,
        "output_tokens": a.output_tokens,
    }
