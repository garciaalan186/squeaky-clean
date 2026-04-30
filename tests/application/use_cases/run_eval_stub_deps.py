"""Stub RunEvalDependencies builder for test_run_eval.

Kept in its own module (not a test file) so the test body can stay
under the 80-line per-file budget.
"""

from pathlib import Path
from typing import cast
from unittest.mock import Mock

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.integration_result import IntegrationResult
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.use_cases.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.use_cases.integrate_module import IntegrateModule
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.application.use_cases.review_security import ReviewSecurity
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.use_cases.validate_architecture import ValidateArchitecture
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.metrics.eval_metric_collector import EvalMetricCollector
from squeaky_clean.infrastructure.testing.test_runner import TestRunner


def _impl() -> ModuleImplementation:
    cls = ClassSpec(name="Operand", pattern="ValueObject", implements=None,
                    methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                       depends=(), classes=(cls,), invariants=())
    ic = ImplementedClass(class_name="Operand", file_path="src/operand.py",
                          code="class Operand:\n    pass\n", test_code=None,
                          cost_usd=0.12, duration_ms=3400,
                          input_tokens=111, output_tokens=222)
    return ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=0.12, total_duration_ms=3400,
                                total_input_tokens=111, total_output_tokens=222, wall_duration_ms=0)


def build_stub_deps() -> RunEvalDependencies:
    """Build a RunEvalDependencies fully stubbed via unittest.mock.Mock."""
    impl = _impl()
    arch = ArchitectureSpec(
        modules=(impl.module,), graph=ArchitectureGraph(edges={}),
    )
    design = Mock(spec=DesignArchitecture, **{
        "execute.return_value": arch,
        "last_raw_notation": "MODULE Calculator\nLAYER Domain\nCLASSES {}\n",
    })
    ta = Mock(spec=GenerateTestArchitecture, **{"execute.return_value":
        TestArchitecture(gherkin_scenarios=(), test_skeletons=())})
    orch = Mock(spec=OrchestrateModule, **{"execute.return_value": impl})
    integ = Mock(spec=IntegrateModule, **{"execute.return_value": IntegrationResult(
        output_dir=Path("/tmp"), files_written=(), test_files_written=())})
    vld = Mock(spec=ValidateArchitecture, **{"execute.return_value":
        ValidationReport(violations=(), files_scanned=0)})
    runner = Mock(spec=TestRunner, **{"run.return_value": TestRunResult(
        passed=2, failed=1, errors=0, duration_ms=99, raw_output="2 passed, 1 failed")})
    sec_review = Mock(spec=ReviewSecurity, **{"execute.return_value":
        SecurityReview(concerns=())})
    sec_tests = Mock(spec=GenerateSecurityTests, **{"execute.return_value":
        TestArchitecture(gherkin_scenarios=(), test_skeletons=())})
    return RunEvalDependencies(
        design_architecture=cast(DesignArchitecture, design),
        generate_test_architecture=cast(GenerateTestArchitecture, ta),
        orchestrate_module=cast(OrchestrateModule, orch),
        integrate_module=cast(IntegrateModule, integ),
        validate_architecture=cast(ValidateArchitecture, vld),
        test_runner=cast(TestRunner, runner),
        metric_collector=EvalMetricCollector(),
        llm_usage_recorder=LLMUsageRecorder(),
        review_security=cast(ReviewSecurity, sec_review),
        generate_security_tests=cast(GenerateSecurityTests, sec_tests),
    )
