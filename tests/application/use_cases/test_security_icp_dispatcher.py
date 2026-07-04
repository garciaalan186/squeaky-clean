"""Tests for SecurityICPDispatcher."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.dtos.security_dispatch_context import SecurityDispatchContext
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.security_icp_dispatcher import SecurityICPDispatcher
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_STUB_CODE = """```python
import pytest
from calculator import Calculator

def test_security_input_validation_calculator() -> None:
    with pytest.raises((ValueError, TypeError)):
        Calculator(0, 0).add(None, None)
```"""

_CLS = ClassSpec(
    name="Calculator", pattern="SimpleClass", implements=None,
    methods=("add(a: float, b: float): float",),
    depends=(), concretes=(), fields=("a: float", "b: float"),
)
_MOD = ModuleSpec(
    name="Calculator", layer=LayerType.DOMAIN, exports=(),
    depends=(), classes=(_CLS,), invariants=(),
)
_PY: LanguageToolkit = LanguageToolkitFactory().for_language(
    TargetLanguage.PYTHON,
)


class _CountingGateway(LLMGateway):
    def __init__(self) -> None:
        self.call_count: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.call_count += 1
        return LLMResponse(_STUB_CODE, 5, 10, 0.001, 20)


def test_dispatch_calls_llm_per_concern() -> None:
    gw = _CountingGateway()
    dispatcher = SecurityICPDispatcher(gw, ModelRouter())
    concerns = (
        SecurityConcern("input_validation", "Calculator", "d1", "t1"),
        SecurityConcern("boundary", "Calculator", "d2", "t2"),
    )
    ctx = SecurityDispatchContext(
        review=SecurityReview(concerns=concerns),
        module=_MOD, toolkit=_PY,
    )
    result = dispatcher.dispatch(ctx)
    assert gw.call_count == 2
    # One skeleton per concern (post-2026-05-10 — keeps each file ≤80 lines)
    assert len(result.test_skeletons) == 2
    assert all(s.class_name == "Calculator" for s in result.test_skeletons)
    paths = {s.file_path for s in result.test_skeletons}
    assert len(paths) == 2  # category slug differentiates the two
    assert any("input_validation" in p for p in paths)
    assert any("boundary" in p for p in paths)


def test_dispatch_empty_concerns_returns_empty() -> None:
    gw = _CountingGateway()
    dispatcher = SecurityICPDispatcher(gw, ModelRouter())
    ctx = SecurityDispatchContext(
        review=SecurityReview(concerns=()),
        module=_MOD, toolkit=_PY,
    )
    result = dispatcher.dispatch(ctx)
    assert gw.call_count == 0
    assert result.test_skeletons == ()
