"""ResumeDispatch: CLI glue that picks problem from checkpoint and runs ResumeRun."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_reader import CheckpointReader
from squeaky_clean.application.evaluation.eval.resume.resume_run import ResumeRun
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.shared.problem.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


class ResumeDispatch:
    """Build deps + load problem then invoke ResumeRun.resume()."""

    def __init__(self) -> None:
        self._reader: CheckpointReader = CheckpointReader()
        self._loader: LoadProblemSpecFromFile = LoadProblemSpecFromFile()
        self._resolver: ProblemResolver = ProblemResolver()

    def resume(
        self, router: ModelRouter, invocation: MaintenanceInvocation,
    ) -> EvalReportBundle:
        """Dispatch a resumed run for ``invocation.resume_run_dir``."""
        run_dir = Path(invocation.resume_run_dir or "")
        problem = self._resolve_problem(run_dir, invocation)
        rc = RunConfigFactory().build(invocation.settings, replicate_id=0)
        deps = DependencyBuilder(router, rc).build(problem)
        return ResumeRun(deps).resume(run_dir, problem)

    def _resolve_problem(
        self, run_dir: Path, invocation: MaintenanceInvocation,
    ) -> ProblemSpec:
        if invocation.problem_file is not None:
            return self._loader.load(Path(invocation.problem_file))
        if invocation.problem_ids:
            return self._resolver.resolve(invocation.problem_ids[0])
        cp_file = run_dir / "CHECKPOINT.json"
        if cp_file.exists():
            data = json.loads(cp_file.read_text())
            pid = str(data.get("problem_id", ""))
            if pid:
                return self._resolver.resolve(pid)
        raise ValueError(
            "cannot resume: no --problem provided and CHECKPOINT.json missing/empty"
        )
