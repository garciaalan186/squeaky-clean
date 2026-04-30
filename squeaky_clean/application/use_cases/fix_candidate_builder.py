"""FixCandidateBuilder: builds FixCandidate tuples from a FixRequest + stems."""

from squeaky_clean.application.dtos.fix_candidate import FixCandidate
from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.fix_failure_mapper import FixFailureMapper

_EXCERPT_CHARS: int = 4000


class FixCandidateBuilder:
    """Assembles FixCandidates by joining mapper output with the ModuleSpec."""

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._mapper: FixFailureMapper = FixFailureMapper(toolkit.language)

    def build(
        self, request: FixRequest, stems: tuple[str, ...],
    ) -> tuple[FixCandidate, ...]:
        """Return a FixCandidate per failing class resolvable to its spec."""
        failing = self._mapper.map(stems, request.implementation.implemented_classes)
        if not failing:
            return ()
        spec_by_name = {c.name: c for c in request.implementation.module.classes}
        excerpt = request.test_run_result.raw_output[-_EXCERPT_CHARS:]
        return tuple(
            FixCandidate(
                original=cls,
                class_spec=spec_by_name[cls.class_name],
                failure_excerpt=excerpt,
                toolkit=self._toolkit,
            )
            for cls in failing
            if cls.class_name in spec_by_name
        )
