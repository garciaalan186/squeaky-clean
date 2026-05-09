"""IntegrationBootstrap port: project skeleton writer per target language."""

from abc import ABC, abstractmethod
from pathlib import Path


class IntegrationBootstrap(ABC):
    """Port for writing per-language project skeleton files once per run.

    Implementations are invoked by IntegrateModule before any class
    files are emitted and are responsible for materializing whatever
    configuration/bootstrap files the target language's test runner
    requires (``conftest.py`` for Python, ``package.json`` for
    JavaScript, etc.).
    """

    @abstractmethod
    def bootstrap(self, output_dir: Path) -> None:
        """Write language-specific project skeleton files under ``output_dir``."""
