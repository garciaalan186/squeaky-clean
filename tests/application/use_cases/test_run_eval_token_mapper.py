"""Tests for RunEvalTokenMapper: per-tier field copies and token totals."""

import pytest

from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.run.run_eval_token_mapper import RunEvalTokenMapper
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _inputs() -> MetricsInputs:
    module = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    impl = ModuleImplementation(module=module, implemented_classes=(),
                                total_cost_usd=0.0, total_duration_ms=0,
                                total_input_tokens=0, total_output_tokens=0,
                                wall_duration_ms=0)
    return MetricsInputs(
        implementation=impl,
        test_run_result=TestRunResult(passed=1, failed=0, errors=0,
                                      duration_ms=1, raw_output=""),
        validation=ValidationReport(violations=(), files_scanned=0),
        architect_input_tokens=100, architect_output_tokens=10,
        architect_cost_usd=0.5, architect_duration_ms=1000,
        test_architect_input_tokens=200, test_architect_output_tokens=20,
        test_architect_cost_usd=0.25, test_architect_duration_ms=2000,
        icp_input_tokens=300, icp_output_tokens=30, icp_cost_usd=0.05,
        icp_duration_ms=3000, icp_wall_duration_ms=1500,
        file_stats=FileStats(avg_line_count=0.0, max_line_count=0,
                             orphan_count=0, artifact_char_count=0),
        security_architect_input_tokens=400,
        security_architect_output_tokens=40,
        security_architect_cost_usd=0.03,
        security_architect_duration_ms=4000,
        classes_fixed=2, fixer_input_tokens=500, fixer_output_tokens=50,
        fixer_cost_usd=0.02, fixer_duration_ms=5000,
    )


def test_apply_copies_per_tier_fields() -> None:
    m = EvalMetrics.empty()
    RunEvalTokenMapper().apply(m, _inputs())
    assert (m.architect_input_tokens, m.architect_output_tokens) == (100, 10)
    assert m.architect_cost_usd == pytest.approx(0.5)
    assert m.architect_duration_ms == 1000
    assert (m.test_architect_input_tokens, m.test_architect_output_tokens) == (200, 20)
    assert (m.icp_input_tokens, m.icp_output_tokens) == (300, 30)
    assert m.icp_wall_duration_ms == 1500
    assert (m.security_architect_input_tokens,
            m.security_architect_output_tokens) == (400, 40)
    assert m.classes_fixed == 2
    assert (m.fixer_input_tokens, m.fixer_output_tokens) == (500, 50)
    assert m.fixer_cost_usd == pytest.approx(0.02)


def test_apply_totals_sum_all_five_tiers() -> None:
    """Totals must include security architect and fixer, not just the big three."""
    m = EvalMetrics.empty()
    RunEvalTokenMapper().apply(m, _inputs())
    assert m.total_tokens_input == 100 + 200 + 300 + 400 + 500
    assert m.total_tokens_output == 10 + 20 + 30 + 40 + 50
