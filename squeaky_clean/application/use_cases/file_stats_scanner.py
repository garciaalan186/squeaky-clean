"""FileStatsScanner: compute FileStats for a generated project tree."""

from pathlib import Path

from squeaky_clean.application.dtos.file_stats import FileStats

_SKIP_NAMES: frozenset[str] = frozenset(
    {"__init__.py", "conftest.py", "package.json", "pom.xml"}
)
_SKIP_DIRS: frozenset[str] = frozenset(
    {"node_modules", "dist", ".git", "__pycache__", "target", "classes"}
)
_EXTS: tuple[str, ...] = (".py", ".js", ".ts", ".java")


class FileStatsScanner:
    """Walks a project dir and computes line-count + orphan-file stats."""

    def scan(self, project_dir: Path) -> FileStats:
        """Return FileStats for every .py/.js file under project_dir."""
        files = self._collect(project_dir)
        if not files:
            return FileStats(0.0, 0, 0, 0)
        contents: dict[Path, str] = {p: p.read_text() for p in files}
        lines = [len(c.splitlines()) for c in contents.values()]
        avg = sum(lines) / len(lines)
        orphans = self._count_orphans(contents)
        char_count = self._artifact_chars(project_dir, contents)
        return FileStats(avg, max(lines), orphans, char_count)

    def _collect(self, project_dir: Path) -> list[Path]:
        if not project_dir.exists():
            return []
        out: list[Path] = []
        for ext in _EXTS:
            for path in sorted(project_dir.rglob(f"*{ext}")):
                if path.name in _SKIP_NAMES:
                    continue
                if any(p in _SKIP_DIRS for p in path.parts):
                    continue
                out.append(path)
        return out

    def _artifact_chars(
        self, root: Path, contents: dict[Path, str]
    ) -> int:
        total = 0
        for path, text in contents.items():
            total += len(text)
            total += len(str(path.relative_to(root)))
        return total

    def _count_orphans(self, contents: dict[Path, str]) -> int:
        total = 0
        for path, _ in contents.items():
            stem = path.stem
            referenced = any(
                stem in text for other, text in contents.items() if other != path
            )
            if not referenced:
                total += 1
        return total
