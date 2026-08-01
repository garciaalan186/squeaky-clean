"""Tests for FixerLoop (R6.2 extraction)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import (
    CheckpointEmitter,
)
from squeaky_clean.application.evaluation.eval.run.stages.fixer_loop import FixerLoop
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import (
    PipelineContext,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def test_green_run_never_invokes_the_fixer(tmp_path: Path) -> None:
    deps = build_stub_deps()
    impl = _impl()
    arch = ArchitectureSpec(modules=(impl.module,), graph=ArchitectureGraph(edges={}))
    problem = ProblemSpec(
        id="P0", slug="p0", description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )

    class _Boom:
        def apply(self, request, output_dir):  # noqa: ANN001, ANN201
            raise AssertionError("fixer must not run on a green suite")

    ctx = PipelineContext(
        problem=problem, output_dir=tmp_path,
        emitter=CheckpointEmitter(problem.id, tmp_path),
        lifecycle=LifecycleTimestampLog(tmp_path), arch=arch,
    )
    green = TestRunResult(passed=3, failed=0, errors=0, duration_ms=1,
                          raw_output="ok")
    run, agg = FixerLoop(deps, _Boom()).run(ctx, green)  # type: ignore[arg-type]
    assert run is green and agg.classes_fixed == 0
