"""CachedDesignArchitecture: DesignArchitecture stand-in returning a cached spec."""

from __future__ import annotations

from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class CachedDesignArchitecture:
    """Stand-in for DesignArchitecture that returns a cached spec."""

    def __init__(self, arch: ArchitectureSpec) -> None:
        self._arch: ArchitectureSpec = arch
        self.last_raw_notation: str = ""

    def execute(self, problem: ProblemSpec) -> ArchitectureSpec:
        del problem
        return self._arch
