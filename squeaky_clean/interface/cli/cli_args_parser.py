"""CLIArgsParser: converts argv into a CLIArgs dataclass via argparse."""

import argparse

from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.flags.cli_args_assembler import CLIArgsAssembler
from squeaky_clean.interface.cli.flags.infra_flag_registrar import InfraFlagRegistrar
from squeaky_clean.interface.cli.flags.maintenance_flag_registrar import (
    MaintenanceFlagRegistrar,
)
from squeaky_clean.interface.cli.flags.recovery_flag_registrar import (
    RecoveryFlagRegistrar,
)
from squeaky_clean.interface.cli.flags.run_flag_registrar import RunFlagRegistrar
from squeaky_clean.interface.cli.flags.sampling_flag_registrar import (
    SamplingFlagRegistrar,
)
from squeaky_clean.interface.cli.flags.security_cache_flag_registrar import (
    SecurityCacheFlagRegistrar,
)

_ALL_PROBLEMS: tuple[str, ...] = (
    "P0", "P0JS", "P0TS", "P0JAVA", "P0GO", "P0RUST",
    "P1", "P1JS", "P1TS", "P1JAVA",
    "P2", "P2JS", "P2TS", "P2JAVA",
    "P3", "P3JS", "P3TS", "P3JAVA",
    "P4", "P5",
)


class CLIArgsParser:
    """Parses a list of CLI arguments into a CLIArgs DTO."""

    def parse(self, argv: list[str]) -> CLIArgs:
        """Return a CLIArgs built from argparse over ``argv``."""
        parser = self._build()
        ns = parser.parse_args(argv)
        ids = self._resolve_ids(ns)
        if self._no_input_mode(ns, ids):
            parser.error(
                "one of --problem, --problems, --sweep, --problem-file, "
                "--recover-from, --triage, --refactor, --squib-file, "
                "--rebuild-dashboard, --micro-evals, or --resume required"
            )
        return CLIArgsAssembler().assemble(ns, ids)

    def _build(self) -> argparse.ArgumentParser:
        # Registrar order is the --help display order: keep it stable
        # (R6.5 decision: the flag surface is a compatibility contract).
        parser = argparse.ArgumentParser(
            prog="squeaky",
            description="Squeaky Clean meta-recursive pipeline CLI",
        )
        RunFlagRegistrar().register(parser)
        SamplingFlagRegistrar().register(parser)
        SecurityCacheFlagRegistrar().register(parser)
        MaintenanceFlagRegistrar().register(parser)
        InfraFlagRegistrar().register(parser)
        RecoveryFlagRegistrar().register(parser)
        return parser

    @staticmethod
    def _no_input_mode(ns: argparse.Namespace, ids: tuple[str, ...]) -> bool:
        return (not ids and not ns.problem_file and not ns.rebuild_dashboard
                and not ns.micro_evals
                and ns.resume_run_dir is None and ns.squib_file is None
                and ns.recover_from is None and ns.triage is None
                and ns.refactor is None)

    def _resolve_ids(self, ns: argparse.Namespace) -> tuple[str, ...]:
        if ns.sweep:
            return _ALL_PROBLEMS
        if ns.problems_csv is not None:
            return tuple(p.strip() for p in str(ns.problems_csv).split(",") if p.strip())
        if ns.problem_id is not None:
            return (str(ns.problem_id),)
        return ()
