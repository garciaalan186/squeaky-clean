"""RunEvalPipeline: sequences the generate->integrate->validate->test stages.

R6.2: formerly a 689-line god-orchestrator; now a thin runner over explicit
stage objects threading a frozen PipelineContext (see eval/run/stages/).
The next harness feature lands as a new stage, not an edit here.
"""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import (
    CheckpointEmitter,
)
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import (
    EvalReportBundle,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import (
    RunEvalDependencies,
)
from squeaky_clean.application.evaluation.eval.run.stages.architecture_gate_stage import (
    ArchitectureGateStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.build_stage import BuildStage
from squeaky_clean.application.evaluation.eval.run.stages.design_stage import (
    DesignStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.emission_stage import (
    EmissionStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.finalize_stage import (
    FinalizeStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.integration_stage import (
    IntegrationStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.metrics_stage import (
    MetricsStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import (
    PipelineContext,
)
from squeaky_clean.application.evaluation.eval.run.stages.tech_spec_stage import (
    TechSpecStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.test_architecture_stage import (
    TestArchitectureStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.test_fix_stage import (
    TestFixStage,
)
from squeaky_clean.application.generation.architecture.architecture_merger import (
    ArchitectureMerger,
)
from squeaky_clean.application.generation.architecture.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.application.generation.repair.compile_gate import CompileGate
from squeaky_clean.application.generation.repair.fixer_stage import FixerStage
from squeaky_clean.application.generation.validation.contract_registry import (
    ContractRegistry,
)
from squeaky_clean.application.shared.gateways.budget_exit_handler import (
    BudgetExitHandler,
)
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)


class RunEvalPipeline:
    """Thin stage runner; budget exhaustion yields a partial report."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps = deps
        merger = ArchitectureMerger()
        orchestrator = OrchestrateArchitecture(deps.orchestrate_module)
        contracts = ContractRegistry()
        fixer = FixerStage(deps.fix_failing_classes, deps.file_system)
        compile_gate = CompileGate(
            deps.project_compiler, fixer, deps.test_repairer,
        )
        self._budget_exit = BudgetExitHandler(deps.cost_gate)
        self._stages = (
            DesignStage(deps),
            ArchitectureGateStage(deps, contracts),
            TestArchitectureStage(deps, merger),
            TechSpecStage(deps, orchestrator),
            EmissionStage(orchestrator, merger),
            IntegrationStage(deps),
            BuildStage(deps, compile_gate),
            TestFixStage(deps, fixer, compile_gate),
        )
        self._metrics = MetricsStage(deps)
        self._finalize = FinalizeStage(deps, contracts)

    def run(self, problem: ProblemSpec, output_dir: Path) -> EvalReportBundle:
        """Execute the full pipeline; on budget exit produce a partial report."""
        try:
            return self._run_to_completion(problem, output_dir)
        except BudgetExceededError as exc:
            return self._budget_exit.handle(problem, output_dir, exc)

    def _run_to_completion(
        self, problem: ProblemSpec, output_dir: Path,
    ) -> EvalReportBundle:
        ctx = PipelineContext(
            problem=problem, output_dir=output_dir,
            emitter=CheckpointEmitter(problem.id, output_dir),
            lifecycle=LifecycleTimestampLog(output_dir),
        )
        for stage in self._stages:
            ctx = stage.run(ctx)
        metrics = self._metrics.build(ctx)
        metrics = self._finalize.finalize(ctx, metrics)
        assert ctx.test_run is not None and ctx.validation is not None
        return EvalReportBundle(
            problem=problem, metrics=metrics,
            test_run_result=ctx.test_run, validation=ctx.validation,
        )
