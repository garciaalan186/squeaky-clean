"""Tests for MetricsStage: counters and stage results folded into EvalMetrics."""

import dataclasses
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.metrics_stage import MetricsStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.stage_counters import StageCounters
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import (
    ModuleImplementation,
)
from squeaky_clean.application.generation.repair.fixer_stage import FixerStageResult
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def _infra_impl() -> ModuleImplementation:
    cls = ClassSpec(name="RedisAdapter", pattern="Adapter", implements=None,
                    methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Cache", layer=LayerType.INFRASTRUCTURE, exports=(),
                        depends=(), classes=(cls,), invariants=())
    ic = ImplementedClass(class_name="RedisAdapter",
                          file_path="src/redis_adapter.py",
                          code="class RedisAdapter:\n    pass\n", test_code=None,
                          cost_usd=0.0, duration_ms=0,
                          input_tokens=0, output_tokens=0)
    return ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=0.0, total_duration_ms=0,
                                total_input_tokens=0, total_output_tokens=0,
                                wall_duration_ms=0)


def _primed_ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    impl = _impl()
    arch = ArchitectureSpec(modules=(impl.module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(
        ctx, arch=arch, impl=impl, module_impls=(impl, _infra_impl()),
        validation=ValidationReport(violations=(), files_scanned=0),
        test_run=TestRunResult(passed=2, failed=1, errors=0,
                               duration_ms=99, raw_output="2 passed, 1 failed"),
        fix_stats=FixerStageResult(0, 0, 0, 0.0, 0, 0),
        sec_arch=TestArchitecture(gherkin_scenarios=(), test_skeletons=()),
        compile_errors=3,
        counters=StageCounters(
            di_violations=1, architect_retries=2, http_violations=4,
            notation_novelty=5, test_criteria_filtered=6,
            infra_explicit=1, infra_derived=2, mcda_runs=2,
            dep_install_failed=True))


def test_counters_fold_into_their_metrics_fields(tmp_path: Path) -> None:
    metrics = MetricsStage(build_stub_deps()).build(_primed_ctx(tmp_path))
    assert metrics.notation.dependency_injection_violations == 1
    assert metrics.reliability.architect_retries == 2
    assert metrics.notation.http_convention_violations == 4
    assert metrics.notation.notation_novelty == 5
    assert metrics.notation.test_criteria_filtered == 6
    assert metrics.notation.infrastructure_choices_explicit == 1
    assert metrics.notation.infrastructure_choices_derived == 2
    assert metrics.notation.mcda_runs == 2
    assert metrics.notation.dependency_install_failed is True
    assert metrics.reliability.compile_errors == 3


def test_stage_results_drive_pass_rate_and_infra_icp_count(tmp_path: Path) -> None:
    metrics = MetricsStage(build_stub_deps()).build(_primed_ctx(tmp_path))
    assert metrics.tests_pass == pytest.approx(2 / 3)
    # Only the INFRASTRUCTURE-layer module impl counts toward the ICP tally.
    assert metrics.notation.infrastructure_icp_count == 1
    assert metrics.notation.spec_conformance_violations == 0
    assert metrics.notation.test_obligation_gaps >= 0
    # No lifecycle events recorded: the builder falls back to ICP durations.
    assert metrics.total_wall_clock_ms == _impl().total_duration_ms
