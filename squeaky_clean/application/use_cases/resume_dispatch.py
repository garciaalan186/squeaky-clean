"""ResumeDispatch: CLI glue that picks problem from checkpoint and runs ResumeRun."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.checkpoint_reader import CheckpointReader
from squeaky_clean.application.use_cases.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)
from squeaky_clean.application.use_cases.resume_run import ResumeRun
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


class ResumeDispatch:
    """Build deps + load problem then invoke ResumeRun.resume()."""

    def __init__(self) -> None:
        self._reader: CheckpointReader = CheckpointReader()
        self._loader: LoadProblemSpecFromFile = LoadProblemSpecFromFile()
        self._resolver: ProblemResolver = ProblemResolver()

    def resume(
        self, router: ModelRouter, args: CLIArgs,
    ) -> EvalReportBundle:
        """Dispatch a resumed run for ``args.resume_run_dir``."""
        run_dir = Path(args.resume_run_dir or "")
        problem = self._resolve_problem(run_dir, args)
        rc = RunConfigFactory().build(args, replicate_id=0)
        deps = DependencyBuilder().build(router, problem, rc)
        return ResumeRun().resume(run_dir, problem, deps)

    def _resolve_problem(self, run_dir: Path, args: CLIArgs) -> ProblemSpec:
        if args.problem_file is not None:
            return self._loader.load(Path(args.problem_file))
        if args.problem_ids:
            return self._resolver.resolve(args.problem_ids[0])
        cp_file = run_dir / "CHECKPOINT.json"
        if cp_file.exists():
            data = json.loads(cp_file.read_text())
            pid = str(data.get("problem_id", ""))
            if pid:
                return self._resolver.resolve(pid)
        raise ValueError(
            "cannot resume: no --problem provided and CHECKPOINT.json missing/empty"
        )
