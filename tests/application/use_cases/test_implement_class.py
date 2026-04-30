"""Tests for ImplementClass use case."""

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)

_CANNED_CODE = '''```python
"""Operand value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Operand:
    value: int
```
'''


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content: str = content
        self.last_request: LLMRequest | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(
            content=self._content,
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.0025,
            duration_ms=1500,
        )


def _assignment() -> ClassAssignment:
    spec = ClassSpec(
        name="Operand",
        pattern="ValueObject",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
    )
    module = ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Operand",),
        depends=(),
        classes=(spec,),
        invariants=(),
    )
    return ClassAssignment(
        class_spec=spec,
        module=module,
        toolkit=_TOOLKIT,
        icp_spec_name="python/ddd_clean/ValueObjectICP",
        file_path="/tmp/p0/src/operand.py",
        test_file_path="/tmp/p0/tests/test_operand.py",
    )


def test_execute_returns_implemented_class() -> None:
    gateway = _StubGateway(_CANNED_CODE)
    uc = ImplementClass(gateway, ModelRouter())
    result = uc.execute(_assignment())
    assert result.class_name == "Operand"
    assert result.file_path == "/tmp/p0/src/operand.py"
    assert "class Operand" in result.code
    assert result.cost_usd == 0.0025
    assert result.duration_ms == 1500


def test_execute_uses_icp_tier_model() -> None:
    gateway = _StubGateway(_CANNED_CODE)
    uc = ImplementClass(gateway, ModelRouter())
    uc.execute(_assignment())
    assert gateway.last_request is not None
    assert gateway.last_request.model == "claude-haiku-4-5-20251001"
    assert "ValueObjectICP" in gateway.last_request.system_prompt
