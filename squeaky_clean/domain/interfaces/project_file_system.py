"""ProjectFileSystem port: abstract interface for generated-project I/O."""

from abc import ABC, abstractmethod
from pathlib import Path


class ProjectFileSystem(ABC):
    """Port for reading, writing, and listing files in generated projects."""

    @abstractmethod
    def read(self, path: Path) -> str:
        """Read the file at `path` and return its contents as text."""

    @abstractmethod
    def write(self, path: Path, content: str) -> None:
        """Write `content` to `path`, creating parent dirs if needed."""

    @abstractmethod
    def list_files(self, root: Path) -> list[Path]:
        """Return a list of files below `root` (recursive)."""
