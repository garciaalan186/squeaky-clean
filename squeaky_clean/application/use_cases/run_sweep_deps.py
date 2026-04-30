"""RunSweepDeps: collaborators required by RunSweep."""

from dataclasses import dataclass
from pathlib import Path

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
