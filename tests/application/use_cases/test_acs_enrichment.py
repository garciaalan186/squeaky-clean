"""Tests for AcsEnrichment (ACS folded into frozen EvalMetrics)."""

import dataclasses
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.acs_enrichment import AcsEnrichment
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl


def _ctx(tmp_path: Path) -> PipelineContext:
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


def test_enrich_populates_acs_and_cost_per_unit(tmp_path: Path) -> None:
    metrics = EvalMetrics(cost=CostBreakdown(estimated_cost_usd=1.0))
    out = AcsEnrichment().enrich(_ctx(tmp_path), metrics)
    assert out.structure.acs_composite > 0
    assert out.structure.acs_normalized == pytest.approx(
        out.structure.acs_composite / 2.5, abs=0.01)
    assert out.structure.acs_cost_per_unit == round(
        1.0 / out.structure.acs_composite, 4)
    # Wall clock is zero for this synthetic run: velocity must stay unset.
    assert out.structure.acs_velocity == 0.0


def test_enrich_returns_new_metrics_and_keeps_input_frozen(
    tmp_path: Path,
) -> None:
    metrics = EvalMetrics.empty()
    out = AcsEnrichment().enrich(_ctx(tmp_path), metrics)
    assert out is not metrics
    assert metrics.structure.acs_composite == 0.0
