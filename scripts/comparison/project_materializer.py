"""Materialize parsed file-blocks to disk under a project root."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.comparison.file_block_parser import ParseResult


@dataclass(frozen=True)
class MaterializeResult:
    """Outcome of writing parsed files to disk."""

    project_dir: Path
    file_count: int
    rejected: tuple[str, ...]   # paths refused for traversing outside project_dir


def materialize(parse: ParseResult, project_dir: Path) -> MaterializeResult:
    """Write each ParsedFile under `project_dir`. Rejects path traversal."""
    project_dir.mkdir(parents=True, exist_ok=True)
    written: int = 0
    rejected: list[str] = []
    for parsed in parse.files:
        target = (project_dir / parsed.path).resolve()
        try:
            target.relative_to(project_dir.resolve())
        except ValueError:
            rejected.append(parsed.path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(parsed.content)
        written += 1
    return MaterializeResult(
        project_dir=project_dir,
        file_count=written,
        rejected=tuple(rejected),
    )
