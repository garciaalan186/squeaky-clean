"""IntegrationResult DTO: paths written by IntegrateModule.execute()."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IntegrationResult:
    """Immutable record of what IntegrateModule actually wrote to disk.

    `output_dir` is the project root that was materialised.
    `files_written` is the sorted tuple of production source files.
    `test_files_written` is the sorted tuple of test files.
    """

    output_dir: Path
    files_written: tuple[Path, ...]
    test_files_written: tuple[Path, ...]
