"""HttpGate: constraint #22 enforcement with one architect retry."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.validation.http_conventions_error import (
    HttpConventionsError,
)
from squeaky_clean.application.generation.validation.validate_http_conventions import (
    validate_http_conventions,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class HttpGate:
    """Enforce constraint #22; retry the architect once, then abort."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        self._logger = deps.run_logger

    def check(self, ctx: PipelineContext) -> tuple[ArchitectureSpec, int, int]:
        """Return (arch, http_violations, architect_retries)."""
        arch = ctx.arch
        assert arch is not None
        violations = validate_http_conventions(arch, ctx.problem)
        if not violations:
            return arch, 0, 0
        for v in violations:
            self._logger.event("http_convention_violation", message=v)
        ctx.output_dir.mkdir(parents=True, exist_ok=True)
        (ctx.output_dir / "HTTP_CONVENTION_VIOLATIONS.txt").write_text(
            "\n".join(violations) + "\n")
        retry_arch = self._deps.design_architecture.execute(
            ctx.problem, prior_violations=violations)
        retry_violations = validate_http_conventions(retry_arch, ctx.problem)
        if retry_violations:
            (ctx.output_dir / "HTTP_CONVENTION_VIOLATIONS.txt").write_text(
                "\n".join(retry_violations) + "\n")
            raise HttpConventionsError(retry_violations)
        return retry_arch, 0, 1
