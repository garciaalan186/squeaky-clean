"""Tests for RepairTestFile: rewrite a test file from an LLM response."""

from pathlib import Path

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.repair_test_file import (
    RepairTestFile,
    TestRepairRequest,
)
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class _FakeGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content = content

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content=self._content, input_tokens=1,
                           output_tokens=1, cost_usd=0.0, duration_ms=0)


def _project(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "foo.ts").write_text("export class Foo {}")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "foo.test.ts").write_text("BROKEN")
    return tmp_path


def _req(tmp_path: Path) -> TestRepairRequest:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.TYPESCRIPT)
    return TestRepairRequest(tmp_path, "tests/foo.test.ts", "err TS2554", tk)


def test_repair_rewrites_file_from_fenced_block(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    gw = _FakeGateway("```typescript\nFIXED CONTENT\n```")
    resp = RepairTestFile(gw, ModelRouter()).repair(_req(proj))
    assert resp is not None
    assert (proj / "tests" / "foo.test.ts").read_text().strip() == "FIXED CONTENT"


def test_repair_leaves_file_when_no_fence(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    gw = _FakeGateway("sorry, no code here")
    RepairTestFile(gw, ModelRouter()).repair(_req(proj))
    assert (proj / "tests" / "foo.test.ts").read_text() == "BROKEN"
