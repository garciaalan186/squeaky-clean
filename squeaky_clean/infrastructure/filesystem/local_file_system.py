"""LocalFileSystem: ProjectFileSystem adapter backed by pathlib."""

from pathlib import Path

from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class LocalFileSystem(ProjectFileSystem):
    """Reads, writes, and lists files on the local disk via pathlib."""

    def read(self, path: Path) -> str:
        """Return the text contents of ``path``."""
        return path.read_text()

    def write(self, path: Path, content: str) -> None:
        """Write ``content`` to ``path``, creating parent dirs as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def list_files(self, root: Path) -> list[Path]:
        """Return every file below ``root`` (recursive), sorted."""
        if not root.exists():
            return []
        return sorted(p for p in root.rglob("*") if p.is_file())
