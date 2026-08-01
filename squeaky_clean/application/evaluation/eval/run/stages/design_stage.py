"""DesignStage: architect execution, layer verify, DI refine, persistence."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.notation_novelty_reporter import (
    NotationNoveltyReporter,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.validation.validate_cross_module_dependencies import (
    validate_cross_module_dependencies,  # noqa: E501
)
from squeaky_clean.application.generation.validation.validate_dependency_injection import (
    validate_dependency_injection,  # noqa: E501
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class DesignStage:
    """Runs the architect; refines via the deterministic DI gate; persists."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._logger = deps.run_logger

    def run(self, ctx: PipelineContext) -> PipelineContext:
        ctx.lifecycle.record("squib_parse_start")
        arch = self._deps.design_architecture.execute(ctx.problem)
        self._verify_layers(arch)
        arch, di_violations, retries = self._refine_di(arch, ctx.problem)
        notation = self._deps.design_architecture.last_raw_notation
        novelty = NotationNoveltyReporter(logger=self._logger).persist(
            ctx.output_dir, notation)
        ctx.emitter.architect_done(notation)
        return replace(ctx, arch=arch, counters=replace(ctx.counters,
            di_violations=di_violations,
            architect_retries=ctx.counters.architect_retries + retries,
            notation_novelty=novelty,
        ))

    def _verify_layers(self, arch: ArchitectureSpec) -> None:
        """Run the opt-in per-layer Verifier pass; log any violations (R1.8)."""
        verifier = self._deps.verify_layer
        if verifier is None:
            return
        for module in arch.modules:
            for violation in verifier.verify(module):
                self._logger.event(
                    "layer_verification_violation",
                    module=module.name, layer=module.layer.value,
                    message=violation,
                )

    def _refine_di(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> tuple[ArchitectureSpec, int, int]:
        """Deterministic DI gate; retry architect once with feedback (non-fatal)."""
        violations = validate_dependency_injection(arch)
        if not violations:
            return arch, 0, 0
        for v in violations:
            self._logger.event("dependency_injection_violation", message=v)
        try:
            retry = self._deps.design_architecture.execute(
                problem, prior_violations=violations)
        except Exception as exc:  # noqa: BLE001
            self._logger.event("di_retry_error", error=str(exc))
            return arch, len(violations), 1
        if validate_cross_module_dependencies(retry):
            self._logger.event("di_retry_discarded", reason="cross_module")
            return arch, len(violations), 1
        retry_violations = validate_dependency_injection(retry)
        if len(retry_violations) < len(violations):
            return retry, len(retry_violations), 1
        self._logger.event("di_retry_discarded", reason="no_improvement")
        return arch, len(violations), 1
