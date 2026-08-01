"""InfraSettings: infrastructure-generation knobs grouped for RunSettings (R6.5)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InfraSettings:
    """H1-H4 infrastructure flags (`--infra`, `--infer-infrastructure`, ...).

    Grouped so RunSettings stays within the 12-field ISP budget; consumed
    only by RunConfigFactory when assembling a RunConfig.
    """

    infrastructure_mode: str = "manual"
    infer_infrastructure: bool = False
    techspec_cache_ttl_days: int = 30
    emit_wiring: bool = True
