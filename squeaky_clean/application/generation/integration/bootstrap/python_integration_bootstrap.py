"""PythonIntegrationBootstrap: writes __init__.py and conftest.py for Python projects."""

from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_CONFTEST_BODY: str = (
    '"""conftest.py: inject project root onto sys.path for src.* imports."""\n'
    "\n"
    "import sys\n"
    "from pathlib import Path\n"
    "\n"
    "_ROOT = Path(__file__).resolve().parent.parent\n"
    "if str(_ROOT) not in sys.path:\n"
    "    sys.path.insert(0, str(_ROOT))\n"
)

_LAYERS: tuple[str, ...] = ("domain", "application", "infrastructure", "interface")


class PythonIntegrationBootstrap(IntegrationBootstrap):
    """Writes Python project skeleton files (__init__.py, conftest.py) per run."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Create ``src/__init__.py``, ``tests/__init__.py``, ``conftest.py``.

        Also seeds an empty ``__init__.py`` at every layer subdir under
        both ``src/`` and ``tests/`` so generated layered packages
        (``src/domain/<module>/...``) are valid Python packages from
        the moment the first ICP file lands.
        """
        self._fs.write(output_dir / "src" / "__init__.py", "")
        self._fs.write(output_dir / "tests" / "__init__.py", "")
        for layer in _LAYERS:
            self._fs.write(output_dir / "src" / layer / "__init__.py", "")
            self._fs.write(output_dir / "tests" / layer / "__init__.py", "")
        self._fs.write(output_dir / "tests" / "conftest.py", _CONFTEST_BODY)
