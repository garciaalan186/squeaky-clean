"""PerArchOnce: helper that returns a cached value for the first module only."""

from __future__ import annotations

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec

_EMPTY = TestArchitecture(gherkin_scenarios=(), test_skeletons=())


class PerArchOnce:
    """Returns a cached value once (for the first module), else the empty arch."""

    def __init__(
        self, cached: TestArchitecture, arch: ArchitectureSpec,
    ) -> None:
        self._first: str = arch.modules[0].name if arch.modules else ""
        self._cached: TestArchitecture = cached

    def take(self, module: ModuleSpec) -> TestArchitecture:
        """Return cached for the first module, EMPTY for the rest."""
        return self._cached if module.name == self._first else _EMPTY
