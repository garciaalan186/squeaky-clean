"""E1 integration: fixer timeout preserves original code, records timeout."""

from squeaky_clean.application.dtos.fix_candidate import FixCandidate
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.fix_one_class import FixOneClass
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class _TimeoutGateway(LLMGateway):
    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content="", input_tokens=0, output_tokens=0,
            cost_usd=0.0, duration_ms=240000, timed_out=True,
        )


def _make_candidate() -> FixCandidate:
    spec = ClassSpec(
        name="Foo",
        pattern="SimpleClass",
        fields=(),
        methods=(),
        depends=(),
        concretes=(),
        invariants=(),
        implements=None,
    )
    original = ImplementedClass(
        class_name="Foo", file_path="src/foo.py",
        code="class Foo:\n    pass\n", test_code=None,
        cost_usd=0.0, duration_ms=0, input_tokens=0, output_tokens=0, retries=0,
    )
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return FixCandidate(
        original=original, class_spec=spec,
        failure_excerpt="some test failed", toolkit=toolkit,
    )


def test_fixer_timeout_keeps_original_code_and_records_timeout() -> None:
    router = ModelRouter({t: "haiku" for t in ModelTier})
    fixer = FixOneClass(_TimeoutGateway(), router)
    candidate = _make_candidate()
    new_cls, response = fixer.execute(candidate)
    assert response.timed_out is True
    assert new_cls.code == candidate.original.code
    recorder = LLMUsageRecorder()
    recorder.record(response, "icp_fixer")
    assert recorder.timeout_count() == 1
