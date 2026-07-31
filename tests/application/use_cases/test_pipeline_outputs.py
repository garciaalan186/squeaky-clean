"""Tests for the PipelineOutputs DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.run.pipeline_outputs import PipelineOutputs
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.repair.fixer_stage_result import FixerStageResult
from squeaky_clean.application.generation.techspec.composer_stats import ComposerStats
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _outputs() -> PipelineOutputs:
    module = ModuleSpec(name="Calc", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    impl = ModuleImplementation(
        module=module, implemented_classes=(), total_cost_usd=0.1,
        total_duration_ms=5, total_input_tokens=10, total_output_tokens=20,
        wall_duration_ms=4,
    )
    return PipelineOutputs(
        implementation=impl,
        test_run=TestRunResult(passed=1, failed=0, errors=0,
                               duration_ms=2, raw_output="ok"),
        validation=ValidationReport(violations=(), files_scanned=1),
        func_run=None,
        security_architecture=TestArchitecture(gherkin_scenarios=(),
                                               test_skeletons=()),
        fix_stats=FixerStageResult(0, 0, 0, 0.0, 0),
    )


def test_composer_stats_and_wall_clock_default() -> None:
    outputs = _outputs()
    assert outputs.composer_stats == ComposerStats()
    assert outputs.composer_stats.validation_failures == 0
    assert outputs.wall_clock_ms == 0


def test_stores_pipeline_components() -> None:
    outputs = _outputs()
    assert outputs.implementation.total_input_tokens == 10
    assert outputs.func_run is None
    assert outputs.fix_stats.classes_fixed == 0
    assert outputs.test_run.passed == 1


def test_is_frozen() -> None:
    outputs = _outputs()
    with pytest.raises(dataclasses.FrozenInstanceError):
        outputs.wall_clock_ms = 9  # type: ignore[misc]
