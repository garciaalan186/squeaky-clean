"""Tests for MetricsInputsAssembler: recorder + outputs -> MetricsInputs."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs_assembler import (
    MetricsInputsAssembler,
)
from squeaky_clean.application.evaluation.eval.metrics.tier_cache_tokens import (
    TierCacheTokens,
)
from squeaky_clean.application.evaluation.eval.run.pipeline_outputs import PipelineOutputs
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.repair.fixer_stage_result import FixerStageResult
from squeaky_clean.application.generation.techspec.composer_stats import ComposerStats
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_skeleton import TestSkeleton
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class _StubRouter(ModelRoutingPolicy):
    """Routes every tier to a predictable model id."""

    def route(self, tier: ModelTier) -> str:
        return f"m-{tier.value}"


def _resp(tok: int, cost: float, ms: int, create: int = 0, read: int = 0,
          hit: bool = False, timeout: bool = False) -> LLMResponse:
    return LLMResponse(content="", input_tokens=tok, output_tokens=tok // 10,
                       cost_usd=cost, duration_ms=ms,
                       cache_creation_input_tokens=create,
                       cache_read_input_tokens=read,
                       cache_hit=hit, timed_out=timeout)


def _recorder() -> LLMUsageRecorder:
    rec = LLMUsageRecorder()
    rec.record(_resp(100, 1.0, 50, create=7, read=3, hit=True), "architect")
    rec.record(_resp(200, 2.0, 60, timeout=True), "test_architect")
    rec.record(_resp(10, 0.25, 5, create=1, read=2), "security_architect")
    rec.record(_resp(20, 0.5, 6), "security_icp")
    rec.record(_resp(50, 0.125, 7, create=11, read=13), "icp")
    rec.record(_resp(10, 0.0, 1, create=2, read=4), "fixer")
    return rec


def _outputs() -> PipelineOutputs:
    module = ModuleSpec(name="Calc", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    impl = ModuleImplementation(
        module=module, implemented_classes=(), total_cost_usd=1.5,
        total_duration_ms=700, total_input_tokens=500,
        total_output_tokens=600, wall_duration_ms=650, total_retries=3,
    )
    skel = TestSkeleton(class_name="Calc", file_path="tests/t.py", code="x")
    return PipelineOutputs(
        implementation=impl,
        test_run=TestRunResult(passed=3, failed=1, errors=0,
                               duration_ms=9, raw_output="3 passed"),
        validation=ValidationReport(violations=(), files_scanned=2),
        func_run=TestRunResult(passed=1, failed=0, errors=0,
                               duration_ms=4, raw_output="1 passed"),
        security_architecture=TestArchitecture(gherkin_scenarios=(),
                                               test_skeletons=(skel, skel)),
        fix_stats=FixerStageResult(classes_fixed=2, input_tokens=30,
                                   output_tokens=40, cost_usd=0.5,
                                   duration_ms=70, passes=1),
        composer_stats=ComposerStats(validation_failures=4,
                                     manager_fallback_calls=5),
        wall_clock_ms=1234,
    )


def _assemble(tmp_path: Path) -> MetricsInputs:
    assembler = MetricsInputsAssembler(_recorder(), _StubRouter())
    return assembler.assemble(_outputs(), tmp_path)


def test_assembles_pipeline_and_per_agent_stats(tmp_path: Path) -> None:
    inputs = _assemble(tmp_path)
    assert inputs.agent_retries == 3
    assert inputs.security_test_count == 2
    assert (inputs.icp_input_tokens, inputs.icp_output_tokens) == (500, 600)
    assert inputs.icp_cost_usd == 1.5
    assert (inputs.icp_duration_ms, inputs.icp_wall_duration_ms) == (700, 650)
    assert (inputs.architect_input_tokens, inputs.architect_output_tokens) == (100, 10)
    assert (inputs.architect_cost_usd, inputs.architect_duration_ms) == (1.0, 50)
    assert (inputs.test_architect_input_tokens, inputs.test_architect_cost_usd) == (200, 2.0)
    # security_architect + security_icp buckets are summed.
    assert (inputs.security_architect_input_tokens,
            inputs.security_architect_output_tokens) == (30, 3)
    assert inputs.security_architect_cost_usd == 0.75
    assert inputs.security_architect_duration_ms == 11
    assert inputs.functional_test_run_result is not None
    assert inputs.functional_test_run_result.passed == 1
    assert inputs.wall_clock_ms == 1234


def test_assembles_cache_timeout_fixer_and_routing_fields(tmp_path: Path) -> None:
    inputs = _assemble(tmp_path)
    assert (inputs.cache_hit_count, inputs.cache_miss_count) == (1, 5)
    assert inputs.cache_creation_input_tokens == 21
    assert inputs.cache_read_input_tokens == 22
    assert inputs.llm_timeouts == 1
    # Per-tier cache tokens: labels are folded into their routing tier,
    # each bucket carrying the model routed for that tier.
    assert inputs.cache_tokens_by_tier == {
        "architect": TierCacheTokens(create_tokens=7, read_tokens=3,
                                     model="m-architect"),
        "manager": TierCacheTokens(create_tokens=1, read_tokens=2,
                                   model="m-manager"),
        "icp": TierCacheTokens(create_tokens=11, read_tokens=13,
                               model="m-icp"),
        "fixer": TierCacheTokens(create_tokens=2, read_tokens=4,
                                 model="m-fixer"),
    }
    assert (inputs.classes_fixed, inputs.fixer_input_tokens,
            inputs.fixer_output_tokens) == (2, 30, 40)
    assert (inputs.fixer_cost_usd, inputs.fixer_duration_ms) == (0.5, 70)
    assert (inputs.composer_validation_failures,
            inputs.composer_manager_fallback_calls) == (4, 5)


def test_scans_output_dir_for_file_stats(tmp_path: Path) -> None:
    inputs = _assemble(tmp_path)
    assert inputs.file_stats == FileStats(0.0, 0, 0, 0)
    (tmp_path / "calc.py").write_text("a = 1\nb = 2\n")
    populated = _assemble(tmp_path)
    assert populated.file_stats.max_line_count == 2
