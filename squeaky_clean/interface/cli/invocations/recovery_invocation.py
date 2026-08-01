"""RecoveryInvocation: config for the architecture-recovery command family (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


@dataclass(frozen=True)
class RecoveryInvocation:
    """Brownfield onboarding flags: recover / triage / refactor / regenerate.

    ``settings`` is carried for the ``--squib-file`` regeneration path, which
    runs the full pipeline and therefore needs a RunConfig.
    """

    squib_file: str | None = None
    legacy_tests: str | None = None
    recover_from: str | None = None
    recover_out: str | None = None
    recover_language: str = "python"
    criteria: tuple[str, ...] = ()
    triage: str | None = None
    refactor: str | None = None
    plan: str | None = None
    refactor_out: str | None = None
    settings: RunSettings = field(default_factory=RunSettings)
