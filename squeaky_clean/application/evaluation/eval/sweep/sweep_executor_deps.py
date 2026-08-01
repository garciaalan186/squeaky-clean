"""SweepExecutorDeps: injected boundary collaborators for the sweep POLICY (R6.7).

The executor lives in application/ and must never import interface/ or
infrastructure/ (layer + component rules are ratcheted). Everything that
crosses those boundaries is injected here by interface/cli/run_sweep:
the per-problem runner (DependencyBuilder + RunEval), the routed model
map for the regression gate, the event logger, and the replay-miss
error type (defined next to the replay cache in infrastructure/llm).
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import RunLogger


@dataclass(frozen=True)
class SweepExecutorDeps:
    """Frozen bundle of boundary-crossing collaborators for SweepExecutor."""

    run_root: Path
    runner: Callable[[ProblemSpec, Path], EvalReportBundle]
    models: Callable[[], dict[str, str]]
    logger: RunLogger
    replay_miss_error: type[Exception]
