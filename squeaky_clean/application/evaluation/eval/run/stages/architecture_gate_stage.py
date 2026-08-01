"""ArchitectureGateStage: hard gates a Squib must pass before emission."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.http_gate import HttpGate
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.cross_module_dependency_error import (  # noqa: E501
    CrossModuleDependencyError,
)
from squeaky_clean.application.generation.validation.contract_fidelity_error import (
    ContractFidelityError,
)
from squeaky_clean.application.generation.validation.contract_registry import ContractRegistry
from squeaky_clean.application.generation.validation.validate_architecture_against_spec import (  # noqa: E501
    SpecConformanceError,
    ValidateArchitectureAgainstSpec,
)
from squeaky_clean.application.generation.validation.validate_contract_fidelity import (
    validate_contract_fidelity,
)
from squeaky_clean.application.generation.validation.validate_cross_module_dependencies import (  # noqa: E501
    validate_cross_module_dependencies,
)
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text


class ArchitectureGateStage:
    """Cross-module, spec-conformance, HTTP-conventions, contract fidelity."""

    def __init__(
        self, deps: RunEvalDependencies, contracts: ContractRegistry,
    ) -> None:
        self._deps = deps
        self._logger = deps.run_logger
        self._contracts = contracts
        self._spec_validator = ValidateArchitectureAgainstSpec()
        self._http = HttpGate(deps)

    def run(self, ctx: PipelineContext) -> PipelineContext:
        arch = ctx.arch
        assert arch is not None
        self._gate(ctx, "cross_module_violation", "CROSS_MODULE_VIOLATIONS.txt",
                   validate_cross_module_dependencies(arch),
                   CrossModuleDependencyError)
        spec_violations = self._spec_validator.execute(arch, ctx.problem)
        if spec_violations:
            raise SpecConformanceError(
                f"architecture violates ProblemSpec semantics: {spec_violations}"
            )
        arch, http_violations, retries = self._http.check(ctx)
        self._gate(ctx, "contract_fidelity_violation",
                   "CONTRACT_FIDELITY_VIOLATIONS.txt",
                   validate_contract_fidelity(arch, ctx.problem, self._contracts),
                   ContractFidelityError)
        return replace(ctx, arch=arch, counters=replace(ctx.counters,
            http_violations=http_violations,
            architect_retries=ctx.counters.architect_retries + retries,
        ))

    def _gate(
        self, ctx: PipelineContext, event: str, artifact: str,
        violations: Sequence[str], error: type[Exception],
    ) -> None:
        if not violations:
            return
        for v in violations:
            self._logger.event(event, message=v)
        atomic_write_text(
            ctx.output_dir / artifact, "\n".join(violations) + "\n")
        raise error(list(violations))
