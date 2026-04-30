"""Tests for GenerateTestArchitecture use case."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.use_cases.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
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

_CANNED = """GHERKIN
---
Feature: Calculator
  Scenario: Addition
    Given operands 2 and 3
    When add is called
    Then result is 5
---

TEST_SKELETONS
---
FILE tests/test_calculator.py
CLASS Calculator
```python
import pytest


def test_add() -> None:
    pytest.fail("not implemented")
```
---
"""


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content: str = content
        self.last_request: LLMRequest | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(self._content, 1, 1, 0.0, 1)


def _p0_module() -> ModuleSpec:
    cls = ClassSpec(
        name="Calculator",
        pattern="SimpleClass",
        implements=None,
        methods=("add(a: int, b: int): int",),
        depends=(),
        concretes=(),
    )
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Calculator",),
        depends=(),
        classes=(cls,),
        invariants=(),
    )


def _deps(gateway: LLMGateway) -> GenerateTestArchitectureDeps:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return GenerateTestArchitectureDeps(
        gateway=gateway,
        router=ModelRouter(),
        toolkit=toolkit,
        recorder=LLMUsageRecorder(),
    )


def test_execute_returns_parsed_test_architecture() -> None:
    gateway = _StubGateway(_CANNED)
    uc = GenerateTestArchitecture(_deps(gateway))
    ctx = TestArchitectureContext(module=_p0_module(), problem=P0)
    ta = uc.execute(ctx)
    assert len(ta.gherkin_scenarios) >= 1
    assert len(ta.test_skeletons) >= 1
    assert ta.test_skeletons[0].class_name == "Calculator"
    assert gateway.last_request is not None
    assert "TestArchitect" in (gateway.last_request.system_prompt or "")


def test_execute_records_token_usage() -> None:
    gateway = _StubGateway(_CANNED)
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    recorder = LLMUsageRecorder()
    deps = GenerateTestArchitectureDeps(
        gateway=gateway, router=ModelRouter(),
        toolkit=toolkit, recorder=recorder,
    )
    ctx = TestArchitectureContext(module=_p0_module(), problem=P0)
    GenerateTestArchitecture(deps).execute(ctx)
    assert recorder.stats("test_architect")[:2] == (1, 1)
    assert recorder.stats()[:2] == (1, 1)
