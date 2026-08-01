"""BuildStage: static validation, dependency install, compile gate."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.repair.compile_gate import (
    CompileGate,
    CompileGateRequest,
)


class BuildStage:
    """Validates the tree, installs dependencies, runs the compile gate."""

    def __init__(self, deps: RunEvalDependencies, gate: CompileGate) -> None:
        self._deps = deps
        self._gate = gate
        self._logger = deps.run_logger

    def run(self, ctx: PipelineContext) -> PipelineContext:
        validation = self._deps.validate_architecture.execute(ctx.output_dir)
        install_failed = self._install(ctx)
        impl = ctx.impl
        assert impl is not None
        result = self._gate.run(CompileGateRequest(
            implementation=impl, output_dir=ctx.output_dir,
            max_passes=int(
                self._deps.run_config.retry_policy.max_fixer_passes),
            architecture=ctx.arch, toolkit=self._deps.toolkit,
        ))
        ctx.lifecycle.record("build_complete")
        return replace(ctx,
            validation=validation,
            compile_errors=result.compile_errors,
            fix_stats=result.fixer,
            counters=replace(ctx.counters, dep_install_failed=install_failed),
        )

    def _install(self, ctx: PipelineContext) -> bool:
        """Run the language installer; True when the install FAILED."""
        installer = self._deps.dependency_installer
        if installer is None:
            return False
        result = installer.install(ctx.output_dir)
        self._logger.event(
            "dependency_install",
            succeeded=result.succeeded, duration_ms=result.duration_ms,
            message=result.message[:500],
        )
        return not result.succeeded
