"""RunEval: allocate a run dir, invoke the pipeline, and write artifacts."""

import json
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.eval_result_dto import EvalResult
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.meta_eval_paths import MetaEvalPaths
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.use_cases.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.application.use_cases.run_eval_report_writer import RunEvalReportWriter
from squeaky_clean.application.use_cases.run_eval_summary_writer import RunEvalSummaryWriter
from squeaky_clean.application.use_cases.run_manifest import RunManifest

# Repository root = parent of squeaky-clean/. Placeholder paths
# anchored relative to this file so the framework runs from any checkout.
_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_RUN_ROOT = _FRAMEWORK_ROOT.parent / "meta-evaluation-results"
_SPEC_DIRS = (_FRAMEWORK_ROOT / "squeaky_clean" / "interface" / "agent_specs",)


class RunEval:
    """Allocates a run directory, runs the pipeline, and writes artifacts."""

    def __init__(
        self,
        deps: RunEvalDependencies,
        run_root: Path | None = None,
    ) -> None:
        self._pipeline: RunEvalPipeline = RunEvalPipeline(deps)
        self._paths: MetaEvalPaths = MetaEvalPaths(run_root or _DEFAULT_RUN_ROOT)
        self._report_writer: RunEvalReportWriter = RunEvalReportWriter()
        self._summary_writer: RunEvalSummaryWriter = RunEvalSummaryWriter()
        self._manifest: RunManifest = RunManifest()

    def execute(self, problem: ProblemSpec) -> EvalResult:
        """Run one problem in a freshly-allocated run dir; write all artifacts."""
        run_dir = self._paths.allocate()
        bundle = self._run_one(problem, run_dir)
        self._summary_writer.write(run_dir / "SUMMARY.md", bundle)
        (run_dir / "metrics.json").write_text(
            json.dumps(asdict(bundle.metrics), indent=2, default=str)
        )
        return self._result(problem, bundle, run_dir)

    def execute_in(
        self, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        """Sweep entry point: run inside a pre-allocated run_dir; no aggregate write."""
        self._paths.adopt(run_dir)
        return self._run_one(problem, run_dir)

    def _run_one(
        self, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        ps_dir = self._paths.problem_set_dir(problem.tier, self._slug(problem))
        bundle = self._pipeline.run(problem, ps_dir)
        self._report_writer.write(ps_dir / "eval_report.json", bundle)
        self._write_post_run_artifacts(ps_dir, run_dir)
        return bundle

    def _write_post_run_artifacts(self, ps_dir: Path, run_dir: Path) -> None:
        """Write the run manifest. Secret scan + SAST run inside the pipeline."""
        del ps_dir  # unused: pipeline writes per-problem security artifacts
        try:
            self._manifest.write(
                run_dir=run_dir,
                models={
                    "architect": "claude-sonnet-4-6",
                    "icp": "claude-haiku-4-5-20251001",
                    "fixer": "claude-sonnet-4-6",
                },
                spec_dirs=_SPEC_DIRS,
                replicate_id=0,
            )
        except OSError:
            pass

    def _result(
        self, problem: ProblemSpec, bundle: EvalReportBundle, run_dir: Path,
    ) -> EvalResult:
        slug = self._slug(problem)
        return EvalResult(
            problem_id=problem.id,
            metrics=bundle.metrics,
            report_path=run_dir / f"problem-set-{problem.tier}-{slug}-code"
            / "eval_report.json",
        )

    @staticmethod
    def _slug(problem: ProblemSpec) -> str:
        """Return language-qualified slug so sweep dirs don't collide."""
        return f"{problem.slug}_{problem.target_language.value}"
