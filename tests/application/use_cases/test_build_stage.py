"""Tests for BuildStage: static validation, install outcome, compile gate."""

import dataclasses
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.build_stage import BuildStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.repair.compile_gate import CompileGate
from squeaky_clean.application.generation.repair.fixer_stage import FixerStage
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.value_objects.install_result import InstallResult
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


class _FailingInstaller(DependencyInstaller):
    """Installer stub whose install always reports failure."""

    def install(self, project_dir: Path) -> InstallResult:
        return InstallResult(succeeded=False, duration_ms=5, message="boom")


def _primed_ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(ctx, impl=_impl())


def _gate() -> CompileGate:
    return CompileGate(None, FixerStage(None, None), None)


def test_sets_validation_compile_errors_and_fix_stats(tmp_path: Path) -> None:
    deps = build_stub_deps()  # no compiler, no installer wired
    ctx = _primed_ctx(tmp_path)
    out = BuildStage(deps, _gate()).run(ctx)
    assert out.validation is not None
    assert out.validation.is_valid
    assert out.compile_errors == 0
    assert out.fix_stats is not None
    assert out.fix_stats.classes_fixed == 0
    assert out.counters.dep_install_failed is False
    lifecycle = (ctx.output_dir / "squib_lifecycle.jsonl").read_text()
    assert "build_complete" in lifecycle


def test_failed_dependency_install_bumps_counter(tmp_path: Path) -> None:
    deps = dataclasses.replace(
        build_stub_deps(), dependency_installer=_FailingInstaller())
    out = BuildStage(deps, _gate()).run(_primed_ctx(tmp_path))
    assert out.counters.dep_install_failed is True
