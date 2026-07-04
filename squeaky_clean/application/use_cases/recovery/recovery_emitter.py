"""RecoveryEmitter: front-half recovery — ingest a project, emit for review."""

from pathlib import Path

from squeaky_clean.application.dtos.recovery.recovery_summary import RecoverySummary
from squeaky_clean.application.use_cases.recovery.criteria_weighting import (
    CriteriaWeighting,
)
from squeaky_clean.application.use_cases.recovery.framework_coupling_detector import (
    FrameworkCouplingDetector,
)
from squeaky_clean.application.use_cases.recovery.layer_assigner import LayerAssigner
from squeaky_clean.application.use_cases.recovery.module_decomposer import ModuleDecomposer
from squeaky_clean.application.use_cases.recovery.pattern_classifier import PatternClassifier
from squeaky_clean.application.use_cases.recovery.python_class_catalog_extractor import (
    PythonClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.refactor_decider import RefactorDecider
from squeaky_clean.application.use_cases.recovery.refactor_proposal_renderer import (
    RefactorProposalRenderer,
)
from squeaky_clean.application.use_cases.recovery.squib_review_gate import SquibReviewGate


class RecoveryEmitter:
    """Ingest a Python project and emit a reviewable Squib plus refactors.

    Runs the deterministic front-half end-to-end — ingest, layer, classify
    (no LLM tie-break here, so the emit is free and reproducible),
    decompose — then writes the Squib for review, a refactor-proposal
    sidecar (Milestone L), and computes the preserve-vs-split MCDA verdict
    (Milestone M) under the user's criteria ranking. No regeneration runs.
    """

    def __init__(self) -> None:
        self._extractor: PythonClassCatalogExtractor = PythonClassCatalogExtractor()
        self._layers: LayerAssigner = LayerAssigner()
        self._patterns: PatternClassifier = PatternClassifier()
        self._decomposer: ModuleDecomposer = ModuleDecomposer()
        self._detector: FrameworkCouplingDetector = FrameworkCouplingDetector()
        self._gate: SquibReviewGate = SquibReviewGate()
        self._renderer: RefactorProposalRenderer = RefactorProposalRenderer()
        self._weighting: CriteriaWeighting = CriteriaWeighting()
        self._decider: RefactorDecider = RefactorDecider()

    def emit(
        self, root: Path, out_path: Path, ranking: tuple[str, ...],
    ) -> RecoverySummary:
        """Emit the Squib + refactor sidecar; return a RecoverySummary."""
        catalog = self._extractor.extract(root)
        layers = self._layers.assign(catalog)
        patterns = self._patterns.classify_all(catalog, layers)
        spec = self._decomposer.decompose(catalog, layers, patterns)
        proposals = self._detector.detect_all(catalog, layers)
        self._gate.emit(spec, out_path)
        refactors = out_path.with_name(out_path.name + ".refactors.md")
        refactors.write_text(self._renderer.render(proposals))
        outcome = self._decider.decide(self._weighting.from_ranking(ranking))
        return RecoverySummary(
            classes=len(catalog.classes), modules=len(spec.modules),
            proposals=len(proposals), recommendation=outcome.winner,
            recommendation_close=outcome.close,
            squib_path=str(out_path), refactors_path=str(refactors),
        )
