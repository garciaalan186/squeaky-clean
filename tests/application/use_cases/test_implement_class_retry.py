"""Tests for ImplementClass retry behavior under RetryPolicy."""

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.dtos.retry_policy import RetryPolicy
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
_GOOD = '''```python
"""Operand."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Operand:
    value: int
```
'''
_BAD = "this is prose, not a fenced block"


class _SequencedGateway(LLMGateway):
    def __init__(self, contents: list[str]) -> None:
        self._contents: list[str] = list(contents)
        self.calls: int = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        idx = min(self.calls, len(self._contents) - 1)
        self.calls += 1
        return LLMResponse(
            content=self._contents[idx], input_tokens=10, output_tokens=10,
            cost_usd=0.001, duration_ms=10,
        )


def _assignment() -> ClassAssignment:
    spec = ClassSpec(name="Operand", pattern="ValueObject", implements=None,
                     methods=(), depends=(), concretes=())
    mod = ModuleSpec(name="Calc", layer=LayerType.DOMAIN, exports=("Operand",),
                     depends=(), classes=(spec,), invariants=())
    return ClassAssignment(
        class_spec=spec, module=mod, toolkit=_TOOLKIT,
        icp_spec_name="python/ddd_clean/ValueObjectICP",
        file_path="/tmp/p0/src/operand.py",
        test_file_path="/tmp/p0/tests/test_operand.py")


def _rc(retries: int) -> RunConfig:
    return RunConfig(
        retry_policy=RetryPolicy(
            max_icp_retries=retries, backoff_base_seconds=0.0),
        cost_budget=CostBudget())


def test_retry_succeeds_on_second_attempt() -> None:
    gw = _SequencedGateway([_BAD, _GOOD])
    uc = ImplementClass(gw, ModelRouter(), _rc(retries=1))
    result = uc.execute(_assignment())
    assert result.class_name == "Operand"
    assert result.retries == 1
    assert gw.calls == 2


def test_no_retry_when_first_call_succeeds() -> None:
    gw = _SequencedGateway([_GOOD])
    uc = ImplementClass(gw, ModelRouter(), _rc(retries=2))
    result = uc.execute(_assignment())
    assert result.retries == 0
    assert gw.calls == 1
