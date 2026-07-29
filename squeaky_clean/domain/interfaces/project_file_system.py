"""ProjectFileSystem port: abstract interface for generated-project I/O."""

from abc import ABC, abstractmethod
from pathlib import Path


class ProjectFileSystem(ABC):
    """Port for reading, writing, and listing files in generated projects.

    Layer boundary (R1.5): writes to USER artifacts — the generated project
    under test — go through this port so they stay testable and swappable.
    Framework-INTERNAL artifacts (the meta-eval reports, dashboards,
    checkpoints, the content-addressed LLM cache, the pricing cache, and the
    lifecycle/observability logs) are deliberately exempt: they are the
    framework's own bookkeeping, not user output, and use direct filesystem I/O
    via ``atomic_write_text``. The handful of remaining application→
    infrastructure imports (model_pricing, content_addressed_cache,
    lifecycle_timestamp_log, tech_spec_builder) are that accepted tier-B
    boundary, tracked in the self-conformance baseline so no NEW ones creep in.
    """

    @abstractmethod
    def read(self, path: Path) -> str:
        """Read the file at `path` and return its contents as text."""

    @abstractmethod
    def write(self, path: Path, content: str) -> None:
        """Write `content` to `path`, creating parent dirs if needed."""

    @abstractmethod
    def list_files(self, root: Path) -> list[Path]:
        """Return a list of files below `root` (recursive)."""
