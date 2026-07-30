"""JavaScriptIntegrationBootstrap: writes package.json for JavaScript projects."""

from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_PACKAGE_JSON: str = '{"type": "module"}\n'


class JavaScriptIntegrationBootstrap(IntegrationBootstrap):
    """Writes a minimal package.json so Node treats the project as ES modules."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Create ``package.json`` at the project root.

        Node's ``--test`` runner auto-discovers ``tests/*.test.js``
        files; no equivalent of conftest.py is required because
        sibling imports use explicit ``../src/name.js`` paths.
        """
        self._fs.write(output_dir / "package.json", _PACKAGE_JSON)
