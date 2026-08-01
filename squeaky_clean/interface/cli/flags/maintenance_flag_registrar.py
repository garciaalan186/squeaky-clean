"""MaintenanceFlagRegistrar: replay, micro-eval, dashboard, resume flags."""

import argparse


class MaintenanceFlagRegistrar:
    """Registers replay-only, micro-eval, dashboard-rebuild, and resume flags."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the micro-eval + maintenance flag block to ``parser``."""
        parser.add_argument(
            "--replay-only", dest="replay_only", action="store_true",
            help="R5.7: serve all LLM calls from cache; any miss fails loudly",
        )
        parser.add_argument(
            "--micro-evals", dest="micro_evals", action="store_true",
            help="R5.4: emit+compile every squib fixture per language; exit",
        )
        parser.add_argument(
            "--micro-patterns", dest="micro_patterns", default="",
            help="R6.1a: only run micro-eval fixtures whose stem starts "
                 "with one of these comma-separated prefixes",
        )
        parser.add_argument(
            "--micro-languages", dest="micro_languages", default="",
            help="R6.1d: only run micro-eval columns for these comma-"
                 "separated language names (e.g. go,rust); default all",
        )
        parser.add_argument(
            "--rebuild-dashboard", dest="rebuild_dashboard",
            action="store_true",
            help="Rebuild meta-evaluation-results/dashboard.html and exit",
        )
        parser.add_argument(
            "--resume", dest="resume_run_dir", default=None,
            help="Resume a partially-completed run from this run dir",
        )
