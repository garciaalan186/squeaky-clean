"""RunInvocation: config for the run/replicate/sweep command family (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


@dataclass(frozen=True)
class RunInvocation:
    """What the eval-run routing needs: which problems, how many times, how.

    Consumed by SqueakyCleanCLI's single/replicated/sweep branches and by
    ReplicateRunner (which reseeds ``settings`` per replicate).
    """

    problem_ids: tuple[str, ...] = ()
    problem_file: str | None = None
    replicates: int = 1
    max_parallel: int = 1
    model_override: str | None = None
    settings: RunSettings = field(default_factory=RunSettings)
