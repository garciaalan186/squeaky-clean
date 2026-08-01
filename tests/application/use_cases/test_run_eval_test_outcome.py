"""Tests for RunEvalTestOutcome (extracted from RunEvalMetricsBuilder)."""

import pytest

from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.run.run_eval_test_outcome import (
    RunEvalTestOutcome,
)
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _impl() -> ModuleImplementation:
    cls = ClassSpec(name="Calc", pattern="ValueObject", implements=None,
                    methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(cls,), invariants=())
    ic = ImplementedClass(class_name="Calc", file_path="src/calc.py",
                          code="class Calc: ...", test_code=None,
                          cost_usd=0.1, duration_ms=100,
                          input_tokens=10, output_tokens=20)
    return ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=0.1, total_duration_ms=1234,
                                total_input_tokens=10, total_output_tokens=20,
                                wall_duration_ms=0)


def _tr(passed: int, failed: int, errors: int) -> TestRunResult:
    return TestRunResult(passed=passed, failed=failed, errors=errors,
                         duration_ms=1, raw_output="")


def _inputs(tr: TestRunResult, fr: TestRunResult | None) -> MetricsInputs:
    return MetricsInputs(
        implementation=_impl(), test_run_result=tr,
        validation=ValidationReport(violations=(), files_scanned=1),
        architect_input_tokens=0, architect_output_tokens=0,
        architect_cost_usd=0.5, architect_duration_ms=0,
        test_architect_input_tokens=0, test_architect_output_tokens=0,
        test_architect_cost_usd=0.25, test_architect_duration_ms=0,
        icp_input_tokens=0, icp_output_tokens=0, icp_cost_usd=0.05,
        icp_duration_ms=0, icp_wall_duration_ms=0,
        file_stats=FileStats(avg_line_count=10.0, max_line_count=40,
                             orphan_count=2, artifact_char_count=400),
        functional_test_run_result=fr,
    )


def test_headline_is_functional_rate_when_functional_run_present() -> None:
    outcome = RunEvalTestOutcome().build(_inputs(_tr(10, 2, 0), _tr(3, 1, 0)))
    assert outcome.tests_pass == pytest.approx(0.75)
    assert outcome.functional_test_count == 4
    assert outcome.security_tests_pass == pytest.approx(7 / 8)


def test_no_functional_run_falls_back_to_overall_rate() -> None:
    outcome = RunEvalTestOutcome().build(_inputs(_tr(9, 1, 0), None))
    assert outcome.tests_pass == pytest.approx(0.9)
    assert outcome.tests_collected == 10


def test_status_build_failed_when_only_errors() -> None:
    outcome = RunEvalTestOutcome().build(_inputs(_tr(0, 0, 3), None))
    assert outcome.test_status == "build_failed"


def test_status_not_measured_when_nothing_collected() -> None:
    outcome = RunEvalTestOutcome().build(_inputs(_tr(0, 0, 0), None))
    assert outcome.test_status == "not_measured"
