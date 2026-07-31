"""Tests for the MetricsInputs DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _inputs() -> MetricsInputs:
    module = ModuleSpec(name="Calc", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    impl = ModuleImplementation(
        module=module, implemented_classes=(), total_cost_usd=0.5,
        total_duration_ms=10, total_input_tokens=100, total_output_tokens=50,
        wall_duration_ms=8,
    )
    return MetricsInputs(
        implementation=impl,
        test_run_result=TestRunResult(passed=1, failed=0, errors=0,
                                      duration_ms=5, raw_output="ok"),
        validation=ValidationReport(violations=(), files_scanned=1),
        architect_input_tokens=1, architect_output_tokens=2,
        architect_cost_usd=0.1, architect_duration_ms=3,
        test_architect_input_tokens=4, test_architect_output_tokens=5,
        test_architect_cost_usd=0.2, test_architect_duration_ms=6,
        icp_input_tokens=7, icp_output_tokens=8, icp_cost_usd=0.3,
        icp_duration_ms=9, icp_wall_duration_ms=10,
        file_stats=FileStats(1.0, 2, 0, 40),
    )


def test_optional_fields_default_to_unmeasured() -> None:
    inputs = _inputs()
    assert inputs.functional_test_run_result is None
    assert inputs.agent_retries == 0
    assert inputs.security_test_count == 0
    assert inputs.classes_fixed == 0
    assert inputs.cache_hit_count == 0
    assert inputs.cache_creation_input_tokens == 0
    assert inputs.llm_timeouts == 0
    assert inputs.cache_create_architect_tokens == 0
    assert inputs.cache_read_fixer_tokens == 0
    assert inputs.architect_model == ""
    assert inputs.fixer_model == ""
    assert inputs.composer_validation_failures == 0
    assert inputs.wall_clock_ms == 0


def test_required_fields_are_stored() -> None:
    inputs = _inputs()
    assert inputs.implementation.total_input_tokens == 100
    assert inputs.icp_wall_duration_ms == 10
    assert inputs.file_stats.max_line_count == 2


def test_is_frozen() -> None:
    inputs = _inputs()
    with pytest.raises(dataclasses.FrozenInstanceError):
        inputs.agent_retries = 5  # type: ignore[misc]
