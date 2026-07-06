"""ProjectCompiler port: compile/typecheck a generated project before tests."""

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.compile_result import CompileResult


class ProjectCompiler(ABC):
    """Port: compile a generated project and report errors + offending files.

    Implemented by per-language adapters (tsc, mvn). Languages without a
    meaningful ahead-of-time compile step (e.g. Python) have no adapter;
    the factory returns ``None`` and the pipeline skips the compile gate.
    """

    @abstractmethod
    def compile(self, project_dir: Path) -> CompileResult:
        """Compile ``project_dir`` and return a parsed CompileResult."""
        raise NotImplementedError
