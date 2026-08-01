"""Tests for HttpGate (R6.2 extraction)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import (
    CheckpointEmitter,
)
from squeaky_clean.application.evaluation.eval.run.stages.http_gate import HttpGate
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import (
    PipelineContext,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def test_clean_architecture_passes_untouched(tmp_path: Path) -> None:
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
    ctx = PipelineContext(
        problem=problem, output_dir=tmp_path,
        emitter=CheckpointEmitter(problem.id, tmp_path),
        lifecycle=LifecycleTimestampLog(tmp_path), arch=arch,
    )
    out_arch, violations, retries = HttpGate(deps).check(ctx)
    assert out_arch is arch and violations == 0 and retries == 0
    assert not (tmp_path / "HTTP_CONVENTION_VIOLATIONS.txt").exists()
