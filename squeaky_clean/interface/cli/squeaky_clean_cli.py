"""SqueakyCleanCLI: top-level CLI wiring that invokes RunEval or RunSweep."""

import sys
from dataclasses import replace
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.recovery.architectural_criterion import (
    ALL_ARCHITECTURAL_CRITERIA,
)
from squeaky_clean.application.dtos.sweep_request import SweepRequest
from squeaky_clean.application.use_cases.html_dashboard_writer import HtmlDashboardWriter
from squeaky_clean.application.use_cases.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)
from squeaky_clean.application.use_cases.metrics_history_aggregator import (
    MetricsHistoryAggregator,
)
from squeaky_clean.application.use_cases.recovery.problem_spec_synthesizer import (
    ProblemSpecSynthesizer,
)
from squeaky_clean.application.use_cases.recovery.recovery_emitter import RecoveryEmitter
from squeaky_clean.application.use_cases.recovery.squib_emitter import SquibEmitter
from squeaky_clean.application.use_cases.recovery.squib_review_gate import (
    SquibReviewGate,
)
from squeaky_clean.application.use_cases.recovery.supplied_architecture_designer import (
    SuppliedArchitectureDesigner,
)
from squeaky_clean.application.use_cases.replicate_runner import ReplicateRunner
from squeaky_clean.application.use_cases.resume_dispatch import ResumeDispatch
from squeaky_clean.application.use_cases.run_eval import RunEval
from squeaky_clean.application.use_cases.run_sweep import RunSweep
from squeaky_clean.application.use_cases.run_sweep_deps import RunSweepDeps
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver
from squeaky_clean.interface.cli.router_factory import RouterFactory
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


class SqueakyCleanCLI:
    """Top-level CLI entry point — single-problem RunEval or parallel RunSweep."""

    def run(self, args: CLIArgs) -> int:
        """Execute the pipeline for ``args`` and return a process exit code.

        Returns 0 on clean completion, 1 on unexpected exception. The
        exit code does NOT reflect pytest pass/fail of the generated
        project — that is recorded in the eval reports.
        """
        self._print_banner(args)
        try:
            if args.rebuild_dashboard:
                return self._rebuild_dashboard()
            router = RouterFactory().build(args.model_override)
            if args.resume_run_dir is not None:
                return self._resume(router, args)
            if args.recover_from is not None:
                return self._recover_emit(args)
            if args.squib_file is not None:
                return self._recover(router, args)
            if args.problem_file is not None:
                problem = LoadProblemSpecFromFile().load(Path(args.problem_file))
                return self._dispatch(router, problem, args)
            if len(args.problem_ids) == 1 and args.max_parallel <= 1:
                return self._single(router, args.problem_ids[0], args)
            return self._sweep(router, args)
        except Exception as exc:  # noqa: BLE001
            print(f"[squeaky] FAILED: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            return 1

    def _single(self, router: object, problem_id: str, args: CLIArgs) -> int:
        return self._dispatch(
            router, ProblemResolver().resolve(problem_id), args,
        )

    def _dispatch(
        self, router: object, problem: ProblemSpec, args: CLIArgs,
    ) -> int:
        if args.replicates > 1:
            return self._replicates(router, problem, args)
        return self._single_spec(router, problem, args)

    def _single_spec(
        self, router: object, problem: ProblemSpec, args: CLIArgs,
    ) -> int:
        rc = RunConfigFactory().build(args, replicate_id=0)
        deps = DependencyBuilder().build(router, problem, rc)  # type: ignore[arg-type]
        result = RunEval(deps).execute(problem)
        print(f"[squeaky] run complete: report at {result.report_path}")
        print(f"[squeaky] tests_pass={result.metrics.tests_pass:.2f} "
              f"cost=${result.metrics.estimated_cost_usd:.4f}")
        return 0

    def _recover(self, router: object, args: CLIArgs) -> int:
        spec = SquibReviewGate().load(Path(str(args.squib_file)))
        tests_dir = Path(args.legacy_tests) if args.legacy_tests else None
        problem = ProblemSpecSynthesizer().synthesize(spec, tests_dir)
        designer = SuppliedArchitectureDesigner(spec, SquibEmitter().emit(spec))
        rc = RunConfigFactory().build(args, replicate_id=0)
        deps = DependencyBuilder().build(router, problem, rc)  # type: ignore[arg-type]
        result = RunEval(replace(deps, design_architecture=designer)).execute(problem)
        print(f"[squeaky] recovery regenerated: report at {result.report_path}")
        return 0

    def _recover_emit(self, args: CLIArgs) -> int:
        out = Path(args.recover_out) if args.recover_out else Path("recovered.squib")
        ranking = args.criteria or ALL_ARCHITECTURAL_CRITERIA
        summary = RecoveryEmitter().emit(Path(args.recover_from), out, ranking)  # type: ignore[arg-type]
        close = " (close call — review)" if summary.recommendation_close else ""
        print(f"[squeaky] recovered {summary.classes} classes into "
              f"{summary.modules} modules -> {summary.squib_path}")
        print(f"[squeaky] {summary.violations} architecture violation(s) "
              f"({summary.coupling_violations} framework-coupling) -> "
              f"{summary.violations_path}")
        print(f"[squeaky] coupled-class recommendation: "
              f"{summary.recommendation}{close}")
        return 0

    def _replicates(
        self, router: object, problem: ProblemSpec, args: CLIArgs,
    ) -> int:
        runner = ReplicateRunner(DependencyBuilder(), RunConfigFactory())
        summary = runner.run(router, problem, args)  # type: ignore[arg-type]
        print(f"[squeaky] replicates complete: {summary.summary_path}")
        return 0

    def _sweep(self, router: object, args: CLIArgs) -> int:
        resolver = ProblemResolver()
        problems = tuple(resolver.resolve(pid) for pid in args.problem_ids)
        deps = RunSweepDeps(
            dependency_builder=DependencyBuilder(),
            router=router,  # type: ignore[arg-type]
        )
        result = RunSweep(deps).execute(SweepRequest(
            problems=problems, max_parallel=args.max_parallel,
        ))
        print(f"[squeaky] sweep complete: {result.run_dir}")
        print(f"[squeaky] {len(result.bundles)} problems, "
              f"${result.total_cost_usd:.4f}, {result.total_duration_ms}ms")
        return 0

    def _resume(self, router: object, args: CLIArgs) -> int:
        bundle = ResumeDispatch().resume(router, args)  # type: ignore[arg-type]
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

    def _print_banner(self, args: CLIArgs) -> None:
        print(f"[squeaky] problems={list(args.problem_ids)} "
              f"max_parallel={args.max_parallel}")
        if args.deterministic:
            print("[squeaky] mode=deterministic (all tiers temp=0, seed=0)")
        if args.model_override is not None:
            print(f"[squeaky] model_override={args.model_override}")
