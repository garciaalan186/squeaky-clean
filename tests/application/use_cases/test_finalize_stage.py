"""Tests for FinalizeStage: ACS enrichment, scans, and the closing checkpoint."""

import dataclasses
import json
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.finalize_stage import FinalizeStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.validation.contract_registry import ContractRegistry
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def _primed_ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    (out / "src").mkdir(exist_ok=True)
    (out / "src" / "operand.py").write_text("class Operand:\n    pass\n")
    arch = ArchitectureSpec(modules=(_impl().module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(ctx, arch=arch)


def _finalize(
    tmp_path: Path, ctx: PipelineContext, metrics: EvalMetrics,
) -> EvalMetrics:
    contracts = ContractRegistry(root=tmp_path / "contracts")
    return FinalizeStage(build_stub_deps(), contracts).finalize(ctx, metrics)


def test_populates_acs_scores_and_cost_per_unit(tmp_path: Path) -> None:
    ctx = _primed_ctx(tmp_path)
    metrics = _finalize(
        tmp_path, ctx,
        EvalMetrics(cost=CostBreakdown(estimated_cost_usd=1.0)),
    )
    s = metrics.structure
    assert s.acs_composite > 0
    assert s.acs_normalized == pytest.approx(s.acs_composite / 2.5, abs=0.01)
    assert s.acs_cost_per_unit == round(1.0 / s.acs_composite, 4)
    # Wall clock is zero for this synthetic run: velocity must stay unset.
    assert s.acs_velocity == 0.0


def test_scans_and_closing_artifacts(tmp_path: Path) -> None:
    ctx = _primed_ctx(tmp_path)
    metrics = _finalize(
        tmp_path, ctx,
        EvalMetrics(cost=CostBreakdown(estimated_cost_usd=0.25)),
    )
    assert metrics.security_scan.secret_leaks_detected == 0
    # Empty usage recorder: no percentile section, so no file written.
    assert not (ctx.output_dir / "LATENCY_PERCENTILES.md").exists()
    # P0 produces no contracts: the registry directory stays empty.
    assert not list((tmp_path / "contracts").glob("*.json"))
    checkpoint = json.loads((ctx.output_dir / "CHECKPOINT.json").read_text())
    assert checkpoint["stage"] == "complete"
    assert checkpoint["cost_spent_usd"] == 0.25
