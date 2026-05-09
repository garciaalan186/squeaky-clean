"""java_packageize: rebase Java source/test files under com/example/."""

from __future__ import annotations

from pathlib import Path


def java_packageize(target: Path, output_dir: Path) -> Path:
    """Force every Java file under ``com/example/`` inside its Maven dir.

    Java's package system IS its layering — the framework's layered
    §Notation paths must be flattened to ``src/main/java/com/example/``
    and ``src/test/java/com/example/``. Non-Java files pass through.
    """
    if target.suffix != ".java":
        return target
    try:
        rel = target.relative_to(output_dir)
    except ValueError:
        return target
    parts = rel.parts
    if len(parts) < 2:
        return target
    if parts[:3] == ("src", "main", "java"):
        roots = ("src", "main", "java")
    elif parts[:3] == ("src", "test", "java"):
        roots = ("src", "test", "java")
    else:
        return target
    fname = parts[-1]
    return output_dir.joinpath(*roots, "com", "example", fname)
