"""IntegrationStage: write the project tree + wiring + manifests + tests."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.manifest_emitter import ManifestEmitter
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.integration.integration_request import IntegrationRequest
from squeaky_clean.application.generation.integration.wiring_generator import WiringGenerator
from squeaky_clean.application.generation.testgen.emit_invariant_tests import EmitInvariantTests
from squeaky_clean.application.shared.language.emit_java_entity_serialization import (
    EmitJavaEntitySerialization,
)
from squeaky_clean.application.shared.language.rewrite_entity_construction import (
    RewriteEntityConstruction,
)
from squeaky_clean.application.shared.language.rewrite_java_field_access import (
    RewriteJavaFieldAccess,
)
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class IntegrationStage:
    """Integrates modules, then emits wiring, manifests, invariant tests."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._logger = deps.run_logger

    def run(self, ctx: PipelineContext) -> PipelineContext:
        arch, impl = ctx.arch, ctx.impl
        assert arch is not None and impl is not None
        assert ctx.test_arch is not None and ctx.sec_arch is not None
        self._deps.integrate_module.execute(IntegrationRequest(
            implementation=impl, test_architecture=ctx.test_arch,
            output_dir=ctx.output_dir,
            security_test_architecture=ctx.sec_arch))
        ctx.emitter.integrated()
        cfg = self._deps.run_config
        if cfg.infrastructure_mode == "auto":
            fs = self._fs()
            if cfg.emit_wiring:
                try:
                    path = WiringGenerator(fs).generate(
                        arch, ctx.tech_specs, ctx.output_dir)
                    self._logger.event("wiring_emitted", path=str(path))
                except OSError as exc:
                    self._logger.event("wiring_emit_failed", error=str(exc))
            ManifestEmitter(self._logger, fs).emit(ctx)
        self._emit_invariant_tests(ctx)
        toolkit = self._deps.toolkit
        if toolkit is not None:
            RewriteEntityConstruction().rewrite(arch, ctx.output_dir, toolkit)
            RewriteJavaFieldAccess().rewrite(arch, ctx.output_dir, toolkit)
            EmitJavaEntitySerialization().emit(arch, ctx.output_dir, toolkit)
        return ctx

    def _fs(self) -> ProjectFileSystem:
        """The injected user-artifact writer (R6.4a: no raw Path writes)."""
        fs = self._deps.file_system
        if fs is None:
            raise ValueError("IntegrationStage requires deps.file_system")
        return fs

    def _emit_invariant_tests(self, ctx: PipelineContext) -> None:
        """Deterministically write construction-raises invariant tests."""
        toolkit = self._deps.toolkit
        if toolkit is None:
            return
        arch = ctx.arch
        assert arch is not None
        fs = self._fs()
        emitted = EmitInvariantTests().emit(arch, ctx.problem, toolkit)
        for rel, body in emitted.items():
            fs.write(ctx.output_dir / rel, body)
