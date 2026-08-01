"""SecurityCacheFlagRegistrar: SAST, security-test, prompt-cache, mode flags."""

import argparse


class SecurityCacheFlagRegistrar:
    """Registers security opt-ins, prompt-cache toggles, and architect mode."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the security + prompt-cache flag block to ``parser``."""
        parser.add_argument("--enable-sast", dest="enable_sast",
                            action="store_true",
                            help="Run bandit SAST over generated code (opt-in)")
        parser.add_argument("--security-tests", dest="enable_security_tests",
                            action="store_true",
                            help="Generate the (spec-grounded) security test "
                                 "layer; off by default so the suite is the "
                                 "acceptance contract")
        cache_group = parser.add_mutually_exclusive_group()
        cache_group.add_argument(
            "--prompt-cache", dest="prompt_cache", action="store_true",
            default=True,
            help="Attach Anthropic ephemeral cache_control (default on)",
        )
        cache_group.add_argument(
            "--no-prompt-cache", dest="prompt_cache", action="store_false",
            help="Disable Anthropic ephemeral cache_control globally",
        )
        parser.add_argument(
            "--prompt-cache-tiers", dest="prompt_cache_tiers",
            default="architect,manager,icp,fixer",
            help="CSV subset of tiers to cache (default: all four)",
        )
        parser.add_argument(
            "--architect-mode", dest="architect_mode", default="patterned",
            choices=("patterned", "scoped", "free"),
            help="R6.9: scoped = DDD mandated, GoF advisory; free = all SimpleClass",
        )
