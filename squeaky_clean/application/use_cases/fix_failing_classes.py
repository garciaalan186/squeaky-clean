"""FixFailingClasses: dispatch Sonnet fixers for classes implicated in test fails."""

from concurrent.futures import ThreadPoolExecutor

from squeaky_clean.application.dtos.fix_candidate import FixCandidate
from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.fix_result import FixResult
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.fix_candidate_builder import FixCandidateBuilder
from squeaky_clean.application.use_cases.fix_failing_classes_deps import (
    FixFailingClassesDeps,
)
from squeaky_clean.application.use_cases.fix_one_class import FixOneClass
from squeaky_clean.application.use_cases.test_failure_parser import TestFailureParser
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_MAX_WORKERS: int = 4
_FIXER_LABEL: str = "icp_fixer"


class FixFailingClasses:
    """Diagnoses failing classes and dispatches Sonnet fixer ICPs in parallel."""

    def __init__(self, deps: FixFailingClassesDeps) -> None:
        self._deps: FixFailingClassesDeps = deps
        self._parser: TestFailureParser = TestFailureParser()
        self._builder: FixCandidateBuilder = FixCandidateBuilder(deps.toolkit)
        self._fixer: FixOneClass = FixOneClass(
            deps.gateway, deps.router, deps.run_config,
        )

    def execute(self, request: FixRequest) -> FixResult:
        """Return FixResult with rewritten classes and fixer-stage usage stats."""
        stems = request.override_stems or self._parser.parse(
            request.test_run_result.raw_output, self._deps.toolkit.language,
        )
        if not stems:
            return self._empty()
        candidates = self._builder.build(request, stems)
        if not candidates:
            return self._empty()
        return self._dispatch(candidates)

    def _dispatch(
        self, candidates: tuple[FixCandidate, ...],
    ) -> FixResult:
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            outputs = list(pool.map(self._fixer.execute, candidates))
        fixed: list[ImplementedClass] = []
        responses: list[LLMResponse] = []
        for cls, resp in outputs:
            fixed.append(cls)
            responses.append(resp)
            self._deps.recorder.record(resp, _FIXER_LABEL)
        return self._aggregate(fixed, responses)

    def _aggregate(
        self, fixed: list[ImplementedClass], responses: list[LLMResponse],
    ) -> FixResult:
        return FixResult(
            fixed_classes=tuple(fixed),
            input_tokens=sum(r.input_tokens for r in responses),
            output_tokens=sum(r.output_tokens for r in responses),
            cost_usd=sum(r.cost_usd for r in responses),
            duration_ms=sum(r.duration_ms for r in responses),
        )

    def _empty(self) -> FixResult:
        return FixResult((), 0, 0, 0.0, 0)
