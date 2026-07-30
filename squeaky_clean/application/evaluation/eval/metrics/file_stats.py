"""FileStats DTO: aggregate file-level stats for a generated project tree."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileStats:
    """Immutable bundle of aggregate source file statistics.

    `avg_line_count` and `max_line_count` are computed across every
    production `.py`/`.js` file under the scanned project, excluding
    harness files (``__init__.py``, ``conftest.py``, ``package.json``).
    `orphan_count` is the number of files whose stem does not appear
    in any other file's imports.
    """

    avg_line_count: float
    max_line_count: int
    orphan_count: int
    artifact_char_count: int
