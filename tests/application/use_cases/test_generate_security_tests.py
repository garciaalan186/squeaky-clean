"""Tests for GenerateSecurityTests use case."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.dtos.security_test_context import SecurityTestContext
from squeaky_clean.application.use_cases.generate_security_tests import GenerateSecurityTests
from squeaky_clean.application.use_cases.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_CANNED = """```python
import pytest
from calculator import Calculator

def test_security_input_validation_calculator() -> None:
    with pytest.raises((ValueError, TypeError)):
        Calculator(0, 0).add(None, None)
```"""

_CLS = ClassSpec(name="Calculator", pattern="SimpleClass", implements=None,
                 methods=("compute(op: str): int",), depends=(), concretes=())
_MOD = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                  depends=(), classes=(_CLS,), invariants=())
_CONCERN = SecurityConcern(category="input_validation", target_class="Calculator",
                           description="Empty input", test_scenario="Pass empty string")
_REVIEW = SecurityReview(concerns=(_CONCERN,))


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content = content
        self.call_count: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.call_count += 1
        return LLMResponse(self._content, 8, 12, 0.002, 40)


def _deps(recorder: LLMUsageRecorder | None = None) -> GenerateTestArchitectureDeps:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return GenerateTestArchitectureDeps(
        gateway=_StubGateway(_CANNED), router=ModelRouter(),
        toolkit=tk, recorder=recorder or LLMUsageRecorder())


def test_execute_returns_test_architecture() -> None:
    ctx = SecurityTestContext(review=_REVIEW, module=_MOD, problem=P0)
    ta = GenerateSecurityTests(_deps()).execute(ctx)
    assert len(ta.test_skeletons) == 1
    assert ta.test_skeletons[0].class_name == "Calculator"
    assert "security" in ta.test_skeletons[0].file_path


def test_execute_records_token_usage() -> None:
    recorder = LLMUsageRecorder()
    ctx = SecurityTestContext(review=_REVIEW, module=_MOD, problem=P0)
    GenerateSecurityTests(_deps(recorder)).execute(ctx)
    assert recorder.stats("security_icp")[:2] == (8, 12)
