"""RecoverCommands: architecture-recovery ingest + regeneration flows."""

from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.generation.recovery.decomposition.problem_spec_synthesizer import (
    ProblemSpecSynthesizer,
)
from squeaky_clean.application.generation.recovery.decomposition.supplied_architecture_designer import (  # noqa: E501
    SuppliedArchitectureDesigner,
)
from squeaky_clean.application.generation.recovery.refactor.architectural_criterion import (
    ALL_ARCHITECTURAL_CRITERIA,
)
from squeaky_clean.application.generation.recovery.refactor.recovery_emitter import RecoveryEmitter
from squeaky_clean.application.generation.recovery.squib.squib_emitter import SquibEmitter
from squeaky_clean.application.generation.recovery.squib.squib_review_gate import (
    SquibReviewGate,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


class RecoverCommands:
    """Executes the --recover-from and --squib-file recovery flows."""

    def regenerate(self, router: ModelRouter, rec: RecoveryInvocation) -> int:
        """Regenerate a project from a signed-off recovery Squib."""
        spec = SquibReviewGate(LocalFileSystem()).load(Path(str(rec.squib_file)))
        tests_dir = Path(rec.legacy_tests) if rec.legacy_tests else None
        problem = ProblemSpecSynthesizer().synthesize(spec, tests_dir)
        designer = SuppliedArchitectureDesigner(spec, SquibEmitter().emit(spec))
        rc = RunConfigFactory().build(rec.settings, replicate_id=0)
        deps = DependencyBuilder(router, rc).build(problem)
        result = RunEval(replace(deps, design_architecture=designer)).execute(problem)
        print(f"[squeaky] recovery regenerated: report at {result.report_path}")
        return 0

    def emit(self, rec: RecoveryInvocation) -> int:
        """Ingest a project and emit the reviewable Squib + violations."""
        out = Path(rec.recover_out) if rec.recover_out else Path("recovered.squib")
        ranking = rec.criteria or ALL_ARCHITECTURAL_CRITERIA
        language = TargetLanguage(rec.recover_language)
        emitter = RecoveryEmitter(LocalFileSystem(), ranking, language)
        summary = emitter.emit(Path(str(rec.recover_from)), out)
        close = " (close call — review)" if summary.recommendation_close else ""
        print(f"[squeaky] recovered {summary.classes} classes into "
              f"{summary.modules} modules -> {summary.squib_path}")
        print(f"[squeaky] {summary.violations} architecture violation(s) "
              f"({summary.coupling_violations} framework-coupling) -> "
              f"{summary.violations_path}")
        print(f"[squeaky] coupled-class recommendation: "
              f"{summary.recommendation}{close}")
        return 0
