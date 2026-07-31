"""MicroEvalCommand: run the pattern x language micro-eval matrix (R5.4)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.meta_eval_paths import MetaEvalPaths
from squeaky_clean.application.evaluation.microeval.micro_eval_deps import MicroEvalDeps
from squeaky_clean.application.evaluation.microeval.micro_eval_report_writer import (
    MicroEvalReportWriter,
)
from squeaky_clean.application.evaluation.microeval.micro_eval_runner import (
    MicroEvalRunner,
)
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.micro_eval_implementers import build_implementers
from squeaky_clean.interface.cli.micro_eval_scaffold import (
    EXTRA_FILES,
    LANGUAGES,
    compilers,
)
from squeaky_clean.interface.cli.router_factory import RouterFactory
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_RUN_ROOT = _FRAMEWORK_ROOT.parent / "meta-evaluation-results"


class MicroEvalCommand:
    """Composition root for `squeaky --micro-evals` (R5.4 middle tier)."""

    def run(self, args: CLIArgs) -> int:
        """Emit + compile every squib fixture in every language; report."""
        rc = RunConfigFactory().build(args, replicate_id=0)
        router = RouterFactory().build(args.model_override)
        run_dir = MetaEvalPaths(_DEFAULT_RUN_ROOT).allocate()
        runner = MicroEvalRunner(MicroEvalDeps(
            implementers=build_implementers(router, rc),
            compilers=compilers(),
            out_root=run_dir / "micro-evals",
            extra_files=EXTRA_FILES,
        ))
        fixtures = sorted(
            (_FRAMEWORK_ROOT / "eval" / "squib_fixtures").glob("*.squib"),
        )
        cells = tuple(
            runner.run_cell(fixture, language)
            for fixture in fixtures for language in LANGUAGES
        )
        md_path = MicroEvalReportWriter().write(run_dir, cells)
        passed = sum(1 for c in cells if c.passed)
        cost = sum(c.cost_usd for c in cells)
        print(f"[squeaky] micro-evals: {passed}/{len(cells)} cells passed, "
              f"${cost:.4f} — {md_path}")
        return 0
