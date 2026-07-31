"""RunSweepDeps: collaborators required by RunSweep."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder


@dataclass(frozen=True)
class RunSweepDeps:
    """Bundle of collaborators RunSweep needs.

    `dependency_builder` is invoked per-problem inside the thread pool so
    each problem gets an isolated gateway/recorder/toolkit graph. `router`
    is shared across problems (model routing is a stateless lookup).
    `run_root` overrides the meta-eval output root (mostly for tests).
    """

    dependency_builder: DependencyBuilder
    router: ModelRouter
    run_root: Path | None = None
    # R5.7: sweep runs previously DROPPED the RunConfig (flags like
    # --replay-only never reached the gateway); None keeps old default.
    run_config: RunConfig | None = None
