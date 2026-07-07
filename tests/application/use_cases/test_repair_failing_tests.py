"""Tests for RepairFailingTests — runtime test-crash repair."""

from pathlib import Path

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.repair_failing_tests import (
    FailingTestsRequest,
    RepairFailingTests,
)
from squeaky_clean.application.use_cases.repair_test_file import RepairTestFile
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_FIXED = "```python\ndef test_x():\n    assert 1 == 1\n```"


class _FakeGateway(LLMGateway):
    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content=_FIXED, input_tokens=1, output_tokens=1,
                           cost_usd=0.1, duration_ms=0)


def _req(tmp_path: Path, output: str) -> FailingTestsRequest:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return FailingTestsRequest(output, tmp_path, tk)


def test_repairs_a_crashing_test(tmp_path: Path) -> None:
    (tmp_path / "test_thing.py").write_text("def test_x():\n    {}.count\n")
    out = "tests/../test_thing.py:2: AttributeError\nFAILED test_thing.py"
    # normalise the path to what exists
    out = "test_thing.py:2: AttributeError"
    repairer = RepairTestFile(_FakeGateway(), ModelRouter())
    result = RepairFailingTests(repairer).run(_req(tmp_path, out))
    assert result.classes_fixed == 1


def test_ignores_plain_assertion_failures(tmp_path: Path) -> None:
    (tmp_path / "test_thing.py").write_text("def test_x():\n    assert False\n")
    out = "test_thing.py:2: AssertionError"
    repairer = RepairTestFile(_FakeGateway(), ModelRouter())
    result = RepairFailingTests(repairer).run(_req(tmp_path, out))
    assert result.classes_fixed == 0  # never rewrite a real assertion away


def test_ignores_source_crashes(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "port.py").write_text("x = 1\n")
    out = "src/port.py:14: NotImplementedError"
    repairer = RepairTestFile(_FakeGateway(), ModelRouter())
    result = RepairFailingTests(repairer).run(_req(tmp_path, out))
    assert result.classes_fixed == 0  # not a test file
