"""SecretPathScanner: recursively scan a directory for secrets and bad files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.use_cases.secret_scanner import SecretScanner

_BINARY_SUFFIXES: frozenset[str] = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".so", ".bin", ".dylib", ".dll",
    ".pyc", ".whl", ".tar", ".gz", ".zip", ".o", ".a",
})
_EXCLUDED_DIRS: frozenset[str] = frozenset({
    ".venv", "venv", "node_modules", "__pycache__", ".git",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "site-packages",
    "cache",
})
_ALLOW_MARKER: str = "secret-scan: allow"
_MAX_BYTES: int = 100 * 1024


@dataclass(frozen=True)
class SecretHit:
    """One detected secret leak with file + line context."""

    path: Path
    line: int
    label: str


class SecretPathScanner:
    """Recursively scan a path tree for secrets via SecretScanner."""

    def __init__(self, scanner: SecretScanner | None = None) -> None:
        self._scanner: SecretScanner = scanner or SecretScanner()

    def scan(self, root: Path) -> tuple[SecretHit, ...]:
        """Walk ``root`` and return all secret hits (filename + content)."""
        hits: list[SecretHit] = []
        if not root.exists():
            return ()
        targets = [root] if root.is_file() else list(root.rglob("*"))
        for path in targets:
            if not path.is_file() or self._excluded(path):
                continue
            hits.extend(self._scan_file(path))
        return tuple(hits)

    @staticmethod
    def _excluded(path: Path) -> bool:
        return any(part in _EXCLUDED_DIRS for part in path.parts)

    def _scan_file(self, path: Path) -> list[SecretHit]:
        hits: list[SecretHit] = []
        label = self._scanner.filename_blocked(path.name)
        if label is not None:
            hits.append(SecretHit(path=path, line=0, label=label))
            return hits
        if path.suffix.lower() in _BINARY_SUFFIXES:
            return hits
        try:
            size = path.stat().st_size
        except OSError:
            return hits
        if size > _MAX_BYTES:
            return hits
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return hits
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _ALLOW_MARKER in line:
                continue
            for found in self._scanner.scan(line):
                hits.append(SecretHit(path=path, line=lineno, label=found))
        return hits
