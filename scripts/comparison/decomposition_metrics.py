"""Compute decomposition-quality metrics from a generated project tree."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DecompositionMetrics:
    """Avg/max file lines + classes-per-module distribution + orphans."""

    avg_file_line_count: float
    max_file_line_count: int
    classes_per_module: tuple[int, ...]
    orphan_files: int


def measure(project_dir: Path) -> DecompositionMetrics:
    """Walk `project_dir/src` to compute decomposition metrics."""
    src = project_dir / "src"
    if not src.exists():
        return DecompositionMetrics(
            avg_file_line_count=0.0,
            max_file_line_count=0,
            classes_per_module=(),
            orphan_files=0,
        )
    py_files = sorted(src.rglob("*.py"))
    if not py_files:
        return DecompositionMetrics(
            avg_file_line_count=0.0,
            max_file_line_count=0,
            classes_per_module=(),
            orphan_files=0,
        )
    sizes = [_line_count(f) for f in py_files]
    classes_per_module = _classes_by_module(py_files, src)
    orphans = _orphan_count(py_files, src)
    return DecompositionMetrics(
        avg_file_line_count=sum(sizes) / len(sizes),
        max_file_line_count=max(sizes),
        classes_per_module=tuple(sorted(classes_per_module.values())),
        orphan_files=orphans,
    )


def _line_count(path: Path) -> int:
    try:
        return sum(1 for _ in path.read_text().splitlines())
    except OSError:
        return 0


def _classes_by_module(py_files: list[Path], src: Path) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for path in py_files:
        rel = path.relative_to(src)
        parts = rel.parts
        module = parts[0] if parts else ""
        counts[module] += _count_classes_in(path)
    return dict(counts)


def _count_classes_in(path: Path) -> int:
    try:
        text = path.read_text()
    except OSError:
        return 0
    return sum(1 for line in text.splitlines() if line.startswith("class "))


def _orphan_count(py_files: list[Path], src: Path) -> int:
    """Count files that no other file in the tree imports.

    Heuristic: a file is non-orphan if any other .py file contains a
    `from <its-module-path>` or `import <its-module-name>` line.
    __init__.py files are never counted as orphans.
    """
    all_text = "\n".join(_safe_read(p) for p in py_files)
    orphans = 0
    for path in py_files:
        if path.name == "__init__.py":
            continue
        rel = path.relative_to(src)
        module_name = path.stem
        dotted = ".".join(rel.with_suffix("").parts)
        needles = [f"from {dotted}", f"import {dotted}", f"from .{module_name}", f"import {module_name}"]
        if not any(n in all_text for n in needles):
            orphans += 1
    return orphans


def _safe_read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""
