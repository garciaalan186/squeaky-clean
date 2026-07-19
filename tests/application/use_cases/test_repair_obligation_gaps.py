"""Tests for RepairObligationGaps — the obligation feedback loop."""

from pathlib import Path

from squeaky_clean.application.dtos.test_obligation import TestObligation
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.repair_obligation_gaps import (
    ObligationRepairRequest,
    RepairObligationGaps,
)
from squeaky_clean.application.use_cases.repair_test_file import RepairTestFile
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_DISCHARGING = (
    "```python\ndef test_x():\n    obj = Ingester()\n"
    "    with pytest.raises(ValueError):\n        obj.ingest_event('')\n```"
)


class _FakeGateway(LLMGateway):
    def __init__(self, content: str) -> None:
        self._content = content

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content=self._content, input_tokens=1,
                           output_tokens=1, cost_usd=0.1, duration_ms=0)


def _ob() -> TestObligation:
    return TestObligation("Ingester", "ingest_event", AssertionKind.RAISES,
                          "", "crit")


def _req(tmp_path: Path) -> ObligationRepairRequest:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return ObligationRepairRequest((_ob(),), tmp_path, tk, 2)


def test_loop_converges_gaps_to_zero(tmp_path: Path) -> None:
    # a test that calls the method but has no raises assertion -> a gap
    (tmp_path / "test_thing.py").write_text(
        "def test_x():\n    obj = Ingester()\n    obj.ingest_event('x')\n")
    repairer = RepairTestFile(_FakeGateway(_DISCHARGING), ModelRouter())
    result = RepairObligationGaps(repairer).run(_req(tmp_path))
    assert result.residual_gaps == 0
    assert result.usage.classes_fixed >= 1


def test_no_repairer_just_reports_residual(tmp_path: Path) -> None:
    (tmp_path / "test_thing.py").write_text(
        "def test_x():\n    Ingester().ingest_event('x')\n")
    result = RepairObligationGaps(None).run(_req(tmp_path))
    assert result.residual_gaps == 1
    assert result.usage.classes_fixed == 0
