"""Tests for RunEvalMetricsBuilder: slice math, headline semantics, status."""

from dataclasses import replace

import pytest

from squeaky_clean.application.evaluation.eval.metrics.file_stats import FileStats
from squeaky_clean.application.evaluation.eval.metrics.metrics_inputs import MetricsInputs
from squeaky_clean.application.evaluation.eval.run.run_eval_metrics_builder import (
    RunEvalMetricsBuilder,
)
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _impl() -> ModuleImplementation:
    cls = ClassSpec(
        name="Calc", pattern="ValueObject", implements=None,
        methods=("add(a: Int): Int", "combine(a: Int, b: Int): Int"),
        depends=(), concretes=(),
    )
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


def test_functional_and_security_slice_math() -> None:
    """Security slice = overall minus functional; both rates computed correctly."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(10, 2, 0), _tr(3, 1, 0)))
    assert m.test_outcome.functional_test_count == 4
    assert m.functional_tests_pass == pytest.approx(0.75)
    # sec_total = 12 - 4 = 8; sec_passed = 10 - 3 = 7
    assert m.security_tests_pass == pytest.approx(7 / 8)
    assert m.test_outcome.tests_collected == 4
    assert m.test_outcome.test_status == "ok"


def test_headline_tests_pass_is_functional_not_blended() -> None:
    """tests_pass must reflect functional acceptance, not the security-diluted blend."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(10, 2, 0), _tr(3, 1, 0)))
    assert m.tests_pass == pytest.approx(0.75)
    assert m.tests_pass != pytest.approx(10 / 12)


def test_security_slice_skipped_when_all_tests_functional() -> None:
    """When the functional run covers every test, no security rate is derived."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(3, 1, 0), _tr(3, 1, 0)))
    assert m.security_tests_pass == 0.0
    assert m.functional_tests_pass == pytest.approx(0.75)


def test_fallback_when_functional_result_is_none() -> None:
    """Without a functional run the overall run doubles as the functional slice."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(3, 1, 0), None))
    assert m.tests_pass == pytest.approx(0.75)
    assert m.functional_tests_pass == pytest.approx(0.75)
    assert m.test_outcome.functional_test_count == 4
    assert m.test_outcome.tests_collected == 4
    assert m.test_outcome.test_status == "ok"


def test_status_build_failed_when_only_errors() -> None:
    """Errors with zero passes/failures classify as build_failed, not a real 0%."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(0, 0, 5), _tr(0, 0, 2)))
    assert m.test_outcome.test_status == "build_failed"
    assert m.tests_pass == 0.0


def test_status_not_measured_when_nothing_collected() -> None:
    """Zero collected tests classify as not_measured (toolchain absent)."""
    m = RunEvalMetricsBuilder().build(_inputs(_tr(0, 0, 0), None))
    assert m.test_outcome.test_status == "not_measured"
    assert m.tests_pass == 0.0


def test_base_aggregates_costs_structure_and_wall_clock() -> None:
    """Cost sums all tiers; structure/file stats and wall-clock fallback apply."""
    inputs = _inputs(_tr(1, 0, 0), None)
    m = RunEvalMetricsBuilder().build(inputs)
    assert m.estimated_cost_usd == pytest.approx(0.5 + 0.25 + 0.05)
    assert m.structure.max_methods_per_class == 2
    assert m.structure.max_args_per_method == 2
    assert m.structure.classes_per_module == (1,)
    assert m.peak_parallelism == 1
    assert m.structure.orphan_files == 2
    assert m.velocity.artifact_token_estimate == 100  # 400 chars // 4
    # wall_clock_ms=0 falls back to the implementation's total duration
    assert m.total_wall_clock_ms == 1234
    m2 = RunEvalMetricsBuilder().build(replace(inputs, wall_clock_ms=5000))
    assert m2.total_wall_clock_ms == 5000
