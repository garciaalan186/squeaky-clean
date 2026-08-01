"""SqueakyCleanCLI: top-level CLI routing that invokes the command flows."""

import sys
import traceback
from pathlib import Path

from squeaky_clean.application.shared.problem.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.commands.maintenance_commands import MaintenanceCommands
from squeaky_clean.interface.cli.commands.recover_commands import RecoverCommands
from squeaky_clean.interface.cli.commands.refactor_commands import RefactorCommands
from squeaky_clean.interface.cli.commands.run_commands import RunCommands
from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.micro_eval_command import MicroEvalCommand
from squeaky_clean.interface.cli.router_factory import RouterFactory


class SqueakyCleanCLI:
    """Top-level CLI entry point — routes a CLIRequest to its command flow."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._log: RunLogger = logger or NullRunLogger()

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
            # event log so failures are diagnosable, not silently discarded.
            self._log.event(
                "cli_run_failed", error=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc(),
            )
            print(f"[squeaky] FAILED: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            return 1

    def _single(self, router: ModelRouter, problem_id: str, run: RunInvocation) -> int:
        return RunCommands(router).single(problem_id, run)

    def _replicated(self, router: ModelRouter, run: RunInvocation) -> int:
        return RunCommands(router).replicated(run)

    def _dispatch(
        self, router: ModelRouter, problem: ProblemSpec, run: RunInvocation,
    ) -> int:
        return RunCommands(router).dispatch(problem, run)

    def _sweep(self, router: ModelRouter, run: RunInvocation) -> int:
        return RunCommands(router).sweep(run)

    def _recover(self, router: ModelRouter, rec: RecoveryInvocation) -> int:
        return RecoverCommands().regenerate(router, rec)

    def _recover_emit(self, rec: RecoveryInvocation) -> int:
        return RecoverCommands().emit(rec)

    def _triage(self, rec: RecoveryInvocation) -> int:
        return RefactorCommands().triage(rec)

    def _refactor_emit(self, rec: RecoveryInvocation) -> int:
        return RefactorCommands().refactor_emit(rec)

    def _resume(self, router: ModelRouter, maint: MaintenanceInvocation) -> int:
        return MaintenanceCommands().resume(router, maint)

    def _rebuild_dashboard(self) -> int:
        return MaintenanceCommands().rebuild_dashboard()

    def _print_banner(self, run: RunInvocation) -> None:
        print(f"[squeaky] problems={list(run.problem_ids)} "
              f"max_parallel={run.max_parallel}")
        if run.settings.deterministic:
            print("[squeaky] mode=deterministic (all tiers temp=0, seed=0)")
        if run.model_override is not None:
            print(f"[squeaky] model_override={run.model_override}")
