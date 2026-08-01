"""MaintenanceInvocation: config for dashboard-rebuild and resume commands (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


@dataclass(frozen=True)
class MaintenanceInvocation:
    """Run-upkeep commands: ``--rebuild-dashboard`` and ``--resume``.

    Resume needs the problem identity (explicit id/file, else the run dir's
    CHECKPOINT.json) plus ``settings`` to rebuild the interrupted RunConfig.
    """

    rebuild_dashboard: bool = False
    resume_run_dir: str | None = None
    problem_ids: tuple[str, ...] = ()
    problem_file: str | None = None
    settings: RunSettings = field(default_factory=RunSettings)
