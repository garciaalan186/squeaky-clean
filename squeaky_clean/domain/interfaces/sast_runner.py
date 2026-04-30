"""SastRunner port: abstract SAST scanner over a generated source tree."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.sast_report import SastReport


class SastRunner(ABC):
    """Port for static-analysis security scanning of generated code."""

    @abstractmethod
    def scan(self, source_dir: Path) -> SastReport:
        """Return a SastReport for files under ``source_dir``.

        Implementations must NOT raise on missing tools; instead return
        an empty report and log a warning so the pipeline can keep running.
        """
