"""IngestScope: decide whether a source path is part of the recovered arch."""

from pathlib import Path

_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".venv", "venv", "node_modules", "site-packages", ".git", "__pycache__",
    "build", "dist", ".tox", ".eggs", ".mypy_cache", ".pytest_cache",
    "migrations", "tests", "test",
})
_EXCLUDED_FILES: frozenset[str] = frozenset({
    "conftest.py", "setup.py", "tests.py", "test.py",
})
_VENDOR_SUFFIXES: tuple[str, ...] = (".egg-info", ".dist-info")


class IngestScope:
    """Filters out test code and vendored/generated files from ingest.

    Recovering an *architecture* means the project's own production code —
    not its test suite, virtualenv, or build artifacts. Test classes are
    genuinely framework-coupled (they subclass TestCase), so leaving them
    in floods the catalog and the coupling detector with noise. This
    excludes conventional test files/dirs and common vendored directories
    while staying language-conventional, not framework-specific.
    """

    def includes(self, path: Path, root: Path) -> bool:
        """Return True if ``path`` should be catalogued as production code."""
        parts = path.relative_to(root).parts
        if any(self._excluded_dir(part) for part in parts[:-1]):
            return False
        name = path.name
        if name in _EXCLUDED_FILES:
            return False
        return not (name.startswith("test_") or name.endswith("_test.py"))

    def _excluded_dir(self, part: str) -> bool:
        return part in _EXCLUDED_DIRS or part.endswith(_VENDOR_SUFFIXES)
