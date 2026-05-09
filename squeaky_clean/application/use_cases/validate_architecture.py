"""ValidateArchitecture: run the architectural rule suite over generated code."""

from pathlib import Path

from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.rule_runner import RuleRunner


class ValidateArchitecture:
    """Use case: inspect a project directory and return a ValidationReport."""

    def __init__(self, rule_runner: RuleRunner, file_extension: str = ".py") -> None:
        self._runner: RuleRunner = rule_runner
        self._glob: str = f"*{file_extension}"

    def execute(self, project_dir: Path) -> ValidationReport:
        """Walk ``project_dir`` and return a ValidationReport of results."""
        violations = self._runner.run(project_dir)
        files_scanned = self._count_files(project_dir)
        return ValidationReport(
            violations=violations,
            files_scanned=files_scanned,
        )

    def _count_files(self, project_dir: Path) -> int:
        if not project_dir.exists():
            return 0
        return sum(1 for p in project_dir.rglob(self._glob) if p.is_file())
