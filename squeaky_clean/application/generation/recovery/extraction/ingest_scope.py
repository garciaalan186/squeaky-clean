"""IngestScope: decide whether a source path is part of the recovered arch."""

from pathlib import Path

_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".venv", "venv", "node_modules", "site-packages", ".git", "__pycache__",
    "build", "dist", ".tox", ".eggs", ".mypy_cache", ".pytest_cache",
    "migrations", "tests", "test", "target", "__tests__", ".gradle", "vendor",
})
_EXCLUDED_FILES: frozenset[str] = frozenset({
    "conftest.py", "setup.py", "tests.py", "test.py",
})
_VENDOR_SUFFIXES: tuple[str, ...] = (".egg-info", ".dist-info")
_TEST_SUFFIXES: tuple[str, ...] = ("Test.java", "Tests.java", "IT.java")


class IngestScope:
    """Filters out test code and vendored/generated files from ingest.

    Recovering an *architecture* means the project's own production code —
    not its test suite, dependency directory, or build artifacts. Test
    classes are genuinely framework-coupled (they subclass TestCase /
    extend a test base), so leaving them in floods the catalog and the
    coupling detector with noise. The patterns are language-conventional
    across Python, JS/TS, and Java — never framework-specific.
    """

    def includes(self, path: Path, root: Path) -> bool:
        """Return True if ``path`` should be catalogued as production code."""
        parts = path.relative_to(root).parts
        if any(self._excluded_dir(part) for part in parts[:-1]):
            return False
        return self._production_file(path.name)

    def _production_file(self, name: str) -> bool:
        if name in _EXCLUDED_FILES:
            return False
        if name.startswith("test_") or name.endswith("_test.py"):
            return False
        lower = name.lower()
        if ".test." in lower or ".spec." in lower:
            return False
        return not name.endswith(_TEST_SUFFIXES)

    def _excluded_dir(self, part: str) -> bool:
        return part in _EXCLUDED_DIRS or part.endswith(_VENDOR_SUFFIXES)
