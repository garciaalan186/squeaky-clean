"""RecoveryFlagRegistrar: architecture-recovery family argparse flags."""

import argparse


class RecoveryFlagRegistrar:
    """Registers squib-file regeneration, recover, triage, and refactor flags."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the recovery flag block to ``parser``."""
        parser.add_argument(
            "--squib-file", dest="squib_file", default=None,
            help="Regenerate from a signed-off recovery Squib, bypassing "
                 "the architect (Agentic Architecture Recovery, Stage 6).",
        )
        parser.add_argument(
            "--legacy-tests", dest="legacy_tests", default=None,
            help="Directory of the brownfield project's tests; acceptance "
                 "criteria are derived from its test_* functions.",
        )
        parser.add_argument(
            "--recover-from", dest="recover_from", default=None,
            help="Ingest a Python project and emit a reviewable Squib + "
                 "refactor sidecar (Architecture Recovery onboarding).",
        )
        parser.add_argument(
            "--recover-out", dest="recover_out", default=None,
            help="Where to write the recovered Squib (default: "
                 "recovered.squib in the cwd).",
        )
        parser.add_argument(
            "--language", dest="recover_language", default="python",
            choices=("python", "javascript", "typescript", "java"),
            help="Source language of the project to recover (default python).",
        )
        parser.add_argument(
            "--criteria", dest="criteria", default=None,
            help="Comma-separated architectural criteria, most-important "
                 "first, driving the preserve-vs-split MCDA verdict.",
        )
        parser.add_argument(
            "--triage", dest="triage", default=None,
            help="Interactively review a violations.json (opt-out per "
                 "category) and write refactor_plan.json.",
        )
        parser.add_argument(
            "--refactor", dest="refactor", default=None,
            help="Apply a --plan refactor_plan.json to a recovered Squib and "
                 "emit the refactored Squib (--refactor-out).",
        )
        parser.add_argument(
            "--plan", dest="plan", default=None,
            help="The refactor_plan.json produced by --triage (required "
                 "with --refactor).",
        )
        parser.add_argument(
            "--refactor-out", dest="refactor_out", default=None,
            help="Where to write the refactored Squib (default: "
                 "refactored.squib).",
        )
