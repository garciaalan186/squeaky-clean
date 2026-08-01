"""Tests for DesignStage: architect run, DI gate counters, persistence."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.design_stage import DesignStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    return PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )


def _di_violating_arch() -> ArchitectureSpec:
    """A UseCase with fields: [] beside a Repository port -> one DI violation."""
    repo = ClassSpec(name="PaymentRepository", pattern="Repository", implements=None,
                     methods=("save(p: Payment): void",), depends=(), concretes=())
    uc = ClassSpec(name="ProcessPayment", pattern="UseCase", implements=None,
                   methods=("process(cmd: Command): Result",), depends=(), concretes=())
    module = ModuleSpec(name="Payment", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(repo, uc), invariants=())
    return ArchitectureSpec(modules=(module,), graph=ArchitectureGraph(edges={}))


def test_clean_arch_sets_ctx_and_persists_notation(tmp_path: Path) -> None:
    deps = build_stub_deps()
    ctx = _ctx(tmp_path)
    out = DesignStage(deps).run(ctx)
    assert out.arch is cast(Mock, deps.design_architecture).execute.return_value
    notation_file = ctx.output_dir / "architecture.notation"
    assert notation_file.read_text() == deps.design_architecture.last_raw_notation
    novelty = json.loads((ctx.output_dir / "notation_novelty.json").read_text())
    assert out.counters.notation_novelty == novelty["count"]
    assert out.counters.di_violations == 0
    assert out.counters.architect_retries == 0
    checkpoint = json.loads((ctx.output_dir / "CHECKPOINT.json").read_text())
    assert checkpoint["stage"] == "architect_done"
    lifecycle = (ctx.output_dir / "squib_lifecycle.jsonl").read_text()
    assert "squib_parse_start" in lifecycle


def test_di_violations_bump_counters_and_retry_once(tmp_path: Path) -> None:
    deps = build_stub_deps()
    design = cast(Mock, deps.design_architecture)
    design.execute.return_value = _di_violating_arch()
    out = DesignStage(deps).run(_ctx(tmp_path))
    # Retry returned an equally-violating arch: original kept, both counted.
    assert out.counters.di_violations == 1
    assert out.counters.architect_retries == 1
    assert design.execute.call_count == 2
    assert design.execute.call_args.kwargs.get("prior_violations")
