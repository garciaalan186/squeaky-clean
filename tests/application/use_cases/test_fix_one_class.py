"""Tests for FixOneClass."""

from squeaky_clean.application.dtos.fix_candidate import FixCandidate
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.fix_one_class import FixOneClass
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)

_FIXED_CODE = '''```python
class Operand:
    def __init__(self, value: int) -> None:
        self.value = value
```
'''


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content = content
        self.last_request: LLMRequest | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(
            content=self._content, input_tokens=80, output_tokens=40,
            cost_usd=0.012, duration_ms=800,
        )


def _candidate() -> FixCandidate:
    spec = ClassSpec(
        name="Operand", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(), fields=("value: int",),
    )
    ModuleSpec(
        name="Calculator", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(spec,), invariants=(),
    )
    original = ImplementedClass(
        class_name="Operand", file_path="/tmp/src/operand.py",
        code="class Operand: pass\n", test_code=None,
        cost_usd=0.003, duration_ms=1500,
        input_tokens=50, output_tokens=30, retries=0,
    )
    return FixCandidate(
        original=original, class_spec=spec,
        failure_excerpt="AssertionError: value missing", toolkit=_TOOLKIT,
    )


def test_execute_returns_fixed_implementation() -> None:
    gw = _StubGateway(_FIXED_CODE)
    fixed, response = FixOneClass(gw, ModelRouter()).execute(_candidate())
    assert fixed.class_name == "Operand"
    assert "def __init__" in fixed.code
    assert response.cost_usd == 0.012
    assert fixed.cost_usd == 0.003 + 0.012
    assert fixed.duration_ms == 1500 + 800


def test_execute_routes_to_fixer_sonnet_tier() -> None:
    gw = _StubGateway(_FIXED_CODE)
    FixOneClass(gw, ModelRouter()).execute(_candidate())
    assert gw.last_request is not None
    assert gw.last_request.model == "claude-sonnet-4-6"


def test_unparseable_response_preserves_original_code() -> None:
    gw = _StubGateway("no fenced block here")
    fixed, _ = FixOneClass(gw, ModelRouter()).execute(_candidate())
    assert fixed.code == "class Operand: pass\n"
