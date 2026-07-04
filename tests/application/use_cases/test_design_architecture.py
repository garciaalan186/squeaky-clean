"""Tests for DesignArchitecture use case."""

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.design_architecture_error import (
    DesignArchitectureError,
)
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_CALC_NOTATION = """MODULE Calculator
LAYER Domain
EXPORTS [Calculator]
DEPENDS []
CLASSES {
  Calculator -> Facade {
    methods: [compute(op: Operation): Number]
    depends: [Operation, Number]
  }
  Operation -> ValueObject {
    fields: [name: str]
    invariants: ["name must be non-empty"]
  }
  Number -> ValueObject {
    fields: [value: float]
    invariants: ["value must be finite"]
  }
}
INVARIANTS ["Division by zero is an error"]
"""


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content: str = content
        self.last_request: LLMRequest | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(
            content=self._content,
            input_tokens=42,
            output_tokens=17,
            cost_usd=0.0,
            duration_ms=1,
        )


def _deps(gateway: LLMGateway) -> LLMCallDeps:
    return LLMCallDeps(
        gateway=gateway, router=ModelRouter(), recorder=LLMUsageRecorder()
    )


def test_execute_returns_parsed_architecture_spec() -> None:
    gateway = _StubGateway(_CALC_NOTATION)
    uc = DesignArchitecture(_deps(gateway))
    arch = uc.execute(P0)
    assert len(arch.modules) >= 1
    first = arch.modules[0]
    assert first.name == "Calculator"
    assert first.layer is LayerType.DOMAIN
    assert {c.name for c in first.classes} == {"Calculator", "Operation", "Number"}
    assert gateway.last_request is not None
    assert "PrincipalArchitect" in (gateway.last_request.system_prompt or "")


def test_execute_records_token_usage() -> None:
    gateway = _StubGateway(_CALC_NOTATION)
    recorder = LLMUsageRecorder()
    deps = LLMCallDeps(
        gateway=gateway, router=ModelRouter(), recorder=recorder
    )
    DesignArchitecture(deps).execute(P0)
    assert recorder.stats("architect")[:2] == (42, 17)
    assert recorder.stats()[:2] == (42, 17)


def test_execute_raises_on_invalid_spec() -> None:
    bad = "MODULE X\nLAYER Domain\nCLASSES { }\n"
    gateway = _StubGateway(bad)
    uc = DesignArchitecture(_deps(gateway))
    with pytest.raises(DesignArchitectureError):
        uc.execute(P0)
