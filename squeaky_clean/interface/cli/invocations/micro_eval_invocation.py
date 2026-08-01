"""MicroEvalInvocation: config for the R5.4 micro-eval matrix command (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


@dataclass(frozen=True)
class MicroEvalInvocation:
    """What MicroEvalCommand consumes: the routing flag, model, run knobs."""

    enabled: bool = False
    model_override: str | None = None
    patterns: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    settings: RunSettings = field(default_factory=RunSettings)
