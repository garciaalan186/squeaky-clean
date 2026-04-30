"""Tests for FixFailingClasses."""

from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.use_cases.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.use_cases.fix_failing_classes_deps import (
    FixFailingClassesDeps,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)

_FIXED = '''```python
class Operand:
    def __init__(self, value: int) -> None:
        self.value = value
```
'''


class _StubGateway(LLMGateway):
    def __init__(self) -> None:
        self.calls: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return LLMResponse(
            content=_FIXED, input_tokens=90, output_tokens=40,
            cost_usd=0.01, duration_ms=500,
        )


def _impl() -> ModuleImplementation:
    spec = ClassSpec(name="Operand", pattern="ValueObject", implements=None,
                     methods=(), depends=(), concretes=(),
                     fields=("value: int",))
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                       depends=(), classes=(spec,), invariants=())
    cls = ImplementedClass(
        class_name="Operand", file_path="src/operand.py",
        code="class Operand: pass\n", test_code=None,
        cost_usd=0.002, duration_ms=900,
        input_tokens=50, output_tokens=20,
    )
    return ModuleImplementation(
        module=module, implemented_classes=(cls,), total_cost_usd=0.002,
        total_duration_ms=900, total_input_tokens=50, total_output_tokens=20,
        wall_duration_ms=900,
    )


def _deps(gateway: LLMGateway, recorder: LLMUsageRecorder) -> FixFailingClassesDeps:
    return FixFailingClassesDeps(
        gateway=gateway, router=ModelRouter(),
        recorder=recorder, toolkit=_TOOLKIT,
    )


def test_execute_fixes_failing_class_and_records_stats() -> None:
    gw, rec = _StubGateway(), LLMUsageRecorder()
    result = FixFailingClasses(_deps(gw, rec)).execute(FixRequest(
        implementation=_impl(),
        test_run_result=TestRunResult(
            passed=0, failed=1, errors=0, duration_ms=10,
            raw_output="FAILED tests/test_operand.py::test_value\n",
        ),
    ))
    assert len(result.fixed_classes) == 1
    assert gw.calls == 1
    assert rec.stats("icp_fixer")[2] == 0.01


def test_execute_returns_empty_when_no_parseable_failures() -> None:
    gw, rec = _StubGateway(), LLMUsageRecorder()
    result = FixFailingClasses(_deps(gw, rec)).execute(FixRequest(
        implementation=_impl(),
        test_run_result=TestRunResult(
            passed=5, failed=0, errors=0, duration_ms=10,
            raw_output="5 passed",
        ),
    ))
    assert result.fixed_classes == ()
    assert gw.calls == 0
