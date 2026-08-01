"""SqueakyCleanCLI: top-level CLI wiring that invokes RunEval or RunSweep."""

import logging
import sys
from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.metrics_history_aggregator import (
    MetricsHistoryAggregator,
)
from squeaky_clean.application.evaluation.eval.report.html_dashboard_writer import (
    HtmlDashboardWriter,
)
from squeaky_clean.application.evaluation.eval.run.run_eval import RunEval
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.generation.recovery.decomposition.interactive_triage import (
    InteractiveTriage,
)
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
from squeaky_clean.application.generation.recovery.refactor.refactor_emitter import RefactorEmitter
from squeaky_clean.application.generation.recovery.refactor.refactor_plan_serializer import (
    RefactorPlanSerializer,
)
from squeaky_clean.application.generation.recovery.scoring.violation_report_deserializer import (
    ViolationReportDeserializer,
)
from squeaky_clean.application.generation.recovery.squib.squib_emitter import SquibEmitter
from squeaky_clean.application.generation.recovery.squib.squib_review_gate import (
    SquibReviewGate,
)
from squeaky_clean.application.shared.problem.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.micro_eval_command import MicroEvalCommand
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver
from squeaky_clean.interface.cli.replicates.replicate_runner import ReplicateRunner
from squeaky_clean.interface.cli.resume_dispatch import ResumeDispatch
from squeaky_clean.interface.cli.router_factory import RouterFactory
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory
from squeaky_clean.interface.cli.run_sweep import RunSweep
from squeaky_clean.interface.cli.run_sweep_deps import RunSweepDeps

_LOG = logging.getLogger(__name__)


class SqueakyCleanCLI:
    """Top-level CLI entry point — single-problem RunEval or parallel RunSweep."""

    def run(self, request: CLIRequest) -> int:
        """Execute the pipeline for ``request`` and return a process exit code.

        Returns 0 on clean completion, 1 on unexpected exception. The
        exit code does NOT reflect pytest pass/fail of the generated
        project — that is recorded in the eval reports.
        """
        run, recovery = request.run, request.recovery
        self._print_banner(run)
        try:
            if request.maintenance.rebuild_dashboard:
                return self._rebuild_dashboard()
            if request.micro_eval.enabled:
                return MicroEvalCommand().run(request.micro_eval)
            if recovery.triage is not None:
                return self._triage(recovery)
            if recovery.refactor is not None:
                return self._refactor_emit(recovery)
            router = RouterFactory().build(run.model_override)
            if request.maintenance.resume_run_dir is not None:
                return self._resume(router, request.maintenance)
            if recovery.recover_from is not None:
                return self._recover_emit(recovery)
            if recovery.squib_file is not None:
                return self._recover(router, recovery)
            if run.problem_file is not None:
                problem = LoadProblemSpecFromFile().load(Path(run.problem_file))
                return self._dispatch(router, problem, run)
            if run.replicates > 1 and run.problem_ids:
                # Replicates route explicitly: the old routing required
                # --max-parallel 1 as well, silently sending --replicates
                # runs through the N=1 sweep path (R5.1).
                return self._replicated(router, run)
            if len(run.problem_ids) == 1 and run.max_parallel <= 1:
                return self._single(router, run.problem_ids[0], run)
            return self._sweep(router, run)
        except Exception as exc:  # noqa: BLE001
            # Keep the 1-line stderr UX, but preserve the full traceback in the
            # log so failures are diagnosable instead of silently discarded.
            _LOG.exception("CLI run failed")
            print(f"[squeaky] FAILED: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            return 1

    def _single(self, router: ModelRouter, problem_id: str, run: RunInvocation) -> int:
        return self._dispatch(
            router, ProblemResolver().resolve(problem_id), run,
        )

    def _replicated(self, router: ModelRouter, run: RunInvocation) -> int:
        """Run every requested problem through the N-replicate path."""
        codes = [
            self._dispatch(router, ProblemResolver().resolve(pid), run)
            for pid in run.problem_ids
        ]
        return max(codes)

    def _dispatch(
        self, router: ModelRouter, problem: ProblemSpec, run: RunInvocation,
    ) -> int:
        if run.replicates > 1:
            return self._replicates(router, problem, run)
        return self._single_spec(router, problem, run)

    def _single_spec(
        self, router: ModelRouter, problem: ProblemSpec, run: RunInvocation,
    ) -> int:
        rc = RunConfigFactory().build(run.settings, replicate_id=0)
        deps = DependencyBuilder().build(router, problem, rc)
        result = RunEval(deps).execute(problem)
        print(f"[squeaky] run complete: report at {result.report_path}")
        print(f"[squeaky] tests_pass={result.metrics.tests_pass:.2f} "
              f"cost=${result.metrics.estimated_cost_usd:.4f}")
        return 0

    def _recover(self, router: ModelRouter, rec: RecoveryInvocation) -> int:
        spec = SquibReviewGate(LocalFileSystem()).load(Path(str(rec.squib_file)))
        tests_dir = Path(rec.legacy_tests) if rec.legacy_tests else None
        problem = ProblemSpecSynthesizer().synthesize(spec, tests_dir)
        designer = SuppliedArchitectureDesigner(spec, SquibEmitter().emit(spec))
        rc = RunConfigFactory().build(rec.settings, replicate_id=0)
        deps = DependencyBuilder().build(router, problem, rc)
        result = RunEval(replace(deps, design_architecture=designer)).execute(problem)
        print(f"[squeaky] recovery regenerated: report at {result.report_path}")
        return 0

    def _recover_emit(self, rec: RecoveryInvocation) -> int:
        out = Path(rec.recover_out) if rec.recover_out else Path("recovered.squib")
        ranking = rec.criteria or ALL_ARCHITECTURAL_CRITERIA
        language = TargetLanguage(rec.recover_language)
        summary = RecoveryEmitter(LocalFileSystem()).emit(
            Path(rec.recover_from), out, ranking, language,  # type: ignore[arg-type]
        )
        close = " (close call — review)" if summary.recommendation_close else ""
        print(f"[squeaky] recovered {summary.classes} classes into "
              f"{summary.modules} modules -> {summary.squib_path}")
        print(f"[squeaky] {summary.violations} architecture violation(s) "
              f"({summary.coupling_violations} framework-coupling) -> "
              f"{summary.violations_path}")
        print(f"[squeaky] coupled-class recommendation: "
              f"{summary.recommendation}{close}")
        return 0

    def _triage(self, rec: RecoveryInvocation) -> int:
        path = Path(str(rec.triage))
        report = ViolationReportDeserializer().deserialize(path.read_text())
        plan = InteractiveTriage().run(report, self._console_ask)
        out = path.with_name("refactor_plan.json")
        out.write_text(RefactorPlanSerializer().serialize(plan))
        print(f"[squeaky] triage complete: {len(plan.fix)} to fix, "
              f"{len(plan.ignore)} ignored -> {out}")
        return 0

    def _refactor_emit(self, rec: RecoveryInvocation) -> int:
        if rec.plan is None:
            print("[squeaky] --refactor requires --plan", file=sys.stderr)
            return 1
        out = Path(rec.refactor_out) if rec.refactor_out else Path("refactored.squib")
        summary = RefactorEmitter(LocalFileSystem()).emit(
            Path(str(rec.refactor)), Path(rec.plan), out,
        )
        print(f"[squeaky] refactored {summary.classes_before} -> "
              f"{summary.classes_after} classes across {summary.modules} "
              f"modules -> {summary.out_path}")
        return 0

    def _console_ask(self, category: str, count: int) -> bool:
        prompt = f"[squeaky] address all {count} {category} violation(s)? [Y/n] "
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            return True
        return answer not in ("n", "no")

    def _replicates(
        self, router: ModelRouter, problem: ProblemSpec, run: RunInvocation,
    ) -> int:
        runner = ReplicateRunner(DependencyBuilder(), RunConfigFactory())
        summary = runner.run(router, problem, run)
        print(f"[squeaky] replicates complete: {summary.summary_path}")
        return 0

    def _sweep(self, router: ModelRouter, run: RunInvocation) -> int:
        resolver = ProblemResolver()
        problems = tuple(resolver.resolve(pid) for pid in run.problem_ids)
        deps = RunSweepDeps(
            dependency_builder=DependencyBuilder(),
            router=router,
            run_config=RunConfigFactory().build(run.settings, replicate_id=0),
        )
        result = RunSweep(deps, JSONLogger()).execute(SweepRequest(
            problems=problems, max_parallel=run.max_parallel,
        ))
        print(f"[squeaky] sweep complete: {result.run_dir}")
        print(f"[squeaky] {len(result.bundles)} problems, "
              f"${result.total_cost_usd:.4f}, {result.total_duration_ms}ms")
        return 0

    def _resume(self, router: ModelRouter, maint: MaintenanceInvocation) -> int:
        bundle = ResumeDispatch().resume(router, maint)
        print(f"[squeaky] resume complete: cost="
              f"${bundle.metrics.estimated_cost_usd:.4f}")
        return 0

    def _rebuild_dashboard(self) -> int:
        framework_root = Path(__file__).resolve().parents[3]
        root = framework_root.parent / "meta-evaluation-results"
        snapshots = MetricsHistoryAggregator().aggregate(root)
        target = root / "dashboard.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        HtmlDashboardWriter().write(snapshots, target)
        print(f"[squeaky] dashboard rebuilt: {target} "
              f"({len(snapshots)} runs)")
        return 0

    def _print_banner(self, run: RunInvocation) -> None:
        print(f"[squeaky] problems={list(run.problem_ids)} "
              f"max_parallel={run.max_parallel}")
        if run.settings.deterministic:
            print("[squeaky] mode=deterministic (all tiers temp=0, seed=0)")
        if run.model_override is not None:
            print(f"[squeaky] model_override={run.model_override}")
