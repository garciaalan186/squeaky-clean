"""Tests for VerifyLayer (R1.8 — the previously-dead LayerVerifier specs)."""

from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.application.use_cases.verify_layer import VerifyLayer
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class _StubGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(
            content=self.content, input_tokens=5, output_tokens=3,
            cost_usd=0.0, duration_ms=1,
        )


def _module() -> ModuleSpec:
    cls = ClassSpec(name="Money", pattern="ValueObject", implements=None,
                    methods=(), depends=(), concretes=())
    return ModuleSpec(name="Payment", layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(cls,), invariants=())


def _deps(gateway: LLMGateway) -> LLMCallDeps:
    return LLMCallDeps(
        gateway=gateway, router=ModelRouter(),
        recorder=LLMUsageRecorder(), run_config=RunConfig(),
    )


def test_ok_response_yields_no_violations() -> None:
    gw = _StubGateway("OK")
    assert VerifyLayer(_deps(gw)).verify(_module()) == ()
    # It loaded the real DomainVerifier spec and sent it as the system prompt.
    assert "DomainVerifier" in gw.calls[0].system_prompt or gw.calls[0].system_prompt


def test_violation_lines_are_parsed() -> None:
    gw = _StubGateway("VIOLATION: Domain imports Application\nVIOLATION: too many args")
    result = VerifyLayer(_deps(gw)).verify(_module())
    assert result == ("Domain imports Application", "too many args")


def test_records_usage_under_manager_tier() -> None:
    gw = _StubGateway("OK")
    recorder = LLMUsageRecorder()
    deps = LLMCallDeps(
        gateway=gw, router=ModelRouter(), recorder=recorder,
        run_config=RunConfig(),
    )
    VerifyLayer(deps).verify(_module())
    assert recorder.stats("manager")[0] > 0  # input tokens recorded
