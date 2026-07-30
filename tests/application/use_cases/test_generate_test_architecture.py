"""Tests for GenerateTestArchitecture use case."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.generation.testgen.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.generation.testgen.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.shared.language.language_toolkit_factory import (
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
    assert "OracleCompiler" in (gateway.last_request.system_prompt or "")


class _SeqGateway(LLMGateway):
    """Returns queued responses in order; records every request."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = responses
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return self._responses[min(len(self.requests) - 1, len(self._responses) - 1)]


def _resp(content: str, truncated: bool = False) -> LLMResponse:
    return LLMResponse(content, 1, 1, 0.0, 1, truncated=truncated)


def _ctx() -> TestArchitectureContext:
    return TestArchitectureContext(module=_p0_module(), problem=P0)


def test_execute_requests_raised_max_tokens() -> None:
    gateway = _SeqGateway([_resp(_CANNED)])
    GenerateTestArchitecture(_deps(gateway)).execute(_ctx())
    assert gateway.requests[0].max_tokens == 8192


def test_execute_retries_on_truncation_then_succeeds() -> None:
    gateway = _SeqGateway([_resp("", truncated=True), _resp(_CANNED)])
    ta = GenerateTestArchitecture(_deps(gateway)).execute(_ctx())
    assert len(ta.test_skeletons) >= 1
    assert len(gateway.requests) == 2
    assert "RETRY" in (gateway.requests[1].user_prompt)


def test_execute_retries_on_parse_error_then_succeeds() -> None:
    gateway = _SeqGateway([_resp("garbage, no sections"), _resp(_CANNED)])
    ta = GenerateTestArchitecture(_deps(gateway)).execute(_ctx())
    assert len(ta.gherkin_scenarios) >= 1
    assert len(gateway.requests) == 2


def test_execute_raises_after_exhausting_retries() -> None:
    import pytest

    from squeaky_clean.application.generation.testgen.generate_test_architecture_error import (
        GenerateTestArchitectureError,
    )
    gateway = _SeqGateway([_resp("still broken")])
    with pytest.raises(GenerateTestArchitectureError):
        GenerateTestArchitecture(_deps(gateway)).execute(_ctx())
    assert len(gateway.requests) == 3  # initial + 2 retries


def test_max_tokens_excluded_from_cache_key() -> None:
    base = LLMRequest(model="m", system_prompt="s", user_prompt="u")
    bumped = LLMRequest(
        model="m", system_prompt="s", user_prompt="u", max_tokens=8192,
    )
    assert base.cache_key() == bumped.cache_key()


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
