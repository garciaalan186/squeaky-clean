"""RunFlagRegistrar: problem-selection and run-shape argparse flags."""

import argparse


class RunFlagRegistrar:
    """Registers --problem/--problems/--sweep plus run-shape flags."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the run-selection flag block to ``parser``."""
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--problem", dest="problem_id", default=None,
                           help="Single problem id (e.g. P0)")
        group.add_argument("--problems", dest="problems_csv", default=None,
                           help="CSV list of problem ids (e.g. P0,P1JS)")
        group.add_argument("--sweep", dest="sweep", action="store_true",
                           help="Run all 16 problems in parallel")
        parser.add_argument("--model-override", dest="model_override",
                            default=None,
                            help="Force all tiers to one model identifier")
        parser.add_argument("--max-parallel", dest="max_parallel", type=int,
                            default=4,
                            help="Concurrent problems in sweep mode (default 4)")
        parser.add_argument("--replicates", dest="replicates", type=int,
                            default=1,
                            help="Number of replicate runs per problem (default 1)")
        parser.add_argument("--problem-file", dest="problem_file", default=None,
                            help="Path to a JSON ProblemSpec file")
