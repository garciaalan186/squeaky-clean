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


class IntegrationStage:
    """Integrates modules, then emits wiring, manifests, invariant tests."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._logger = deps.run_logger
        self._wiring = WiringGenerator()
        self._manifests = ManifestEmitter(deps.run_logger)

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
        if cfg.infrastructure_mode == "auto" and cfg.emit_wiring:
            try:
                path = self._wiring.generate(
                    arch, ctx.tech_specs, ctx.output_dir)
                self._logger.event("wiring_emitted", path=str(path))
            except OSError as exc:
                self._logger.event("wiring_emit_failed", error=str(exc))
        if cfg.infrastructure_mode == "auto":
            self._manifests.emit(ctx)
        self._emit_invariant_tests(ctx)
        toolkit = self._deps.toolkit
        if toolkit is not None:
            RewriteEntityConstruction().rewrite(arch, ctx.output_dir, toolkit)
            RewriteJavaFieldAccess().rewrite(arch, ctx.output_dir, toolkit)
            EmitJavaEntitySerialization().emit(arch, ctx.output_dir, toolkit)
        return ctx

    def _emit_invariant_tests(self, ctx: PipelineContext) -> None:
        """Deterministically write construction-raises invariant tests."""
        toolkit = self._deps.toolkit
        if toolkit is None:
            return
        arch = ctx.arch
        assert arch is not None
        emitted = EmitInvariantTests().emit(arch, ctx.problem, toolkit)
        for rel, body in emitted.items():
            path = ctx.output_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
