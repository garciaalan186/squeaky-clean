"""DependencyInstaller port: install all declared deps for a generated project."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult


class DependencyInstaller(ABC):
    """Port for invoking a per-language package manager before tests run.

    Adapters MUST be best-effort: they never raise on toolchain absence
    or timeout; instead they log + return ``InstallResult(succeeded=False,
    ...)`` so the pipeline can keep running in degraded mode.
    """

    @abstractmethod
    def install(self, project_dir: Path) -> InstallResult:
        """Install all declared dependencies in ``project_dir``.

        Returns success + log; never raises on toolchain absence (logs
        + returns failed).
        """
