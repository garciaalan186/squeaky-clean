"""CLIRequest: the four per-command invocation configs, post-parse (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.invocations.micro_eval_invocation import MicroEvalInvocation
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation


@dataclass(frozen=True)
class CLIRequest:
    """Composition-root assembly of the invocation objects (ISP: consumers
    downstream of SqueakyCleanCLI.run() each receive only their own slice)."""

    run: RunInvocation = field(default_factory=RunInvocation)
    recovery: RecoveryInvocation = field(default_factory=RecoveryInvocation)
    micro_eval: MicroEvalInvocation = field(default_factory=MicroEvalInvocation)
    maintenance: MaintenanceInvocation = field(default_factory=MaintenanceInvocation)
