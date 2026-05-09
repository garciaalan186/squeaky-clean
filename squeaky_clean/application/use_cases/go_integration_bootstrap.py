"""GoIntegrationBootstrap: writes .gitignore for Go projects."""

from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_GITIGNORE: str = "vendor/\n*.test\n*.out\n"


class GoIntegrationBootstrap(IntegrationBootstrap):
    """Writes a Go project skeleton (.gitignore) and ensures the output dir exists."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Ensure ``output_dir`` exists and seed a ``.gitignore``.

        Go uses a single-package layout plus ``go.mod``, so no
        ``__init__.py`` chain is required. A ``.gitignore`` keeps
        compiled test binaries and the optional ``vendor/`` directory
        out of source control. ``go.mod`` is generated separately by
        the wiring pipeline.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        self._fs.write(output_dir / ".gitignore", _GITIGNORE)
