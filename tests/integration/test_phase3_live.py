"""Live integration test for Phase 3: TestArchitect against the real Claude CLI."""

import os

import pytest

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
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_SKIP_REASON = "Set RUN_INTEGRATION_TESTS=1 to enable live LLM calls"


class _RecordingGateway(LLMGateway):
    def __init__(self, inner: LLMGateway) -> None:
        self._inner: LLMGateway = inner
        self.last: LLMResponse | None = None

    def complete(self, request: LLMRequest) -> LLMResponse:
        response = self._inner.complete(request)
        self.last = response
        return response


def _p0_module() -> ModuleSpec:
    methods = (
        "add(a: Number, b: Number): Number",
        "subtract(a: Number, b: Number): Number",
        "divide(a: Number, b: Number): Number",
    )
    calc = ClassSpec("Calculator", "Facade", None, methods, ("Number",), ())
    num = ClassSpec("Number", "ValueObject", None, (), (), ())
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Calculator",),
        depends=(),
        classes=(calc, num),
        invariants=("Division by zero is an error",),
    )


@pytest.mark.integration
def test_generate_test_architecture_live() -> None:
    if os.environ.get("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip(_SKIP_REASON)
    recorder = _RecordingGateway(ClaudeCLIGateway())
    router = ModelRouter({
        ModelTier.ARCHITECT: "claude-sonnet-4-6",
        ModelTier.MANAGER: "claude-sonnet-4-6",
        ModelTier.ICP: "claude-haiku-4-5-20251001",
    })
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    deps = GenerateTestArchitectureDeps(
        gateway=recorder, router=router, toolkit=toolkit,
        recorder=LLMUsageRecorder(),
    )
    uc = GenerateTestArchitecture(deps)
    ctx = TestArchitectureContext(module=_p0_module(), problem=P0)
    ta = uc.execute(ctx)
    assert len(ta.test_skeletons) >= 1
    assert len(ta.gherkin_scenarios) >= 1
    assert recorder.last is not None
    print(
        f"\n[phase3-live] scenarios={len(ta.gherkin_scenarios)} "
        f"skeletons={len(ta.test_skeletons)} "
        f"cost_usd={recorder.last.cost_usd} "
        f"duration_ms={recorder.last.duration_ms} "
        f"input_tokens={recorder.last.input_tokens} "
        f"output_tokens={recorder.last.output_tokens}"
    )
    for s in ta.test_skeletons:
        print(f"[phase3-live] skeleton class={s.class_name} file={s.file_path}")
