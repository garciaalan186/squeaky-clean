"""RecoveryEmitter: front-half recovery — ingest a project, emit for review."""

from pathlib import Path

from squeaky_clean.application.generation.recovery.decomposition.layer_assigner import LayerAssigner
from squeaky_clean.application.generation.recovery.decomposition.module_decomposer import (
    ModuleDecomposer,
)
from squeaky_clean.application.generation.recovery.extraction.class_catalog_extractor_factory import (  # noqa: E501
    ClassCatalogExtractorFactory,
)
from squeaky_clean.application.generation.recovery.refactor.criteria_weighting import (
    CriteriaWeighting,
)
from squeaky_clean.application.generation.recovery.refactor.recovery_artifact import (
    RecoveryArtifact,
)
from squeaky_clean.application.generation.recovery.refactor.recovery_summary import RecoverySummary
from squeaky_clean.application.generation.recovery.refactor.refactor_decider import RefactorDecider
from squeaky_clean.application.generation.recovery.scoring.pattern_classifier import (
    PatternClassifier,
)
from squeaky_clean.application.generation.recovery.scoring.violation_analysis import (
    ViolationAnalysis,
)
from squeaky_clean.application.generation.recovery.scoring.violation_report_renderer import (
    ViolationReportRenderer,
)
from squeaky_clean.application.generation.recovery.scoring.violation_report_serializer import (
    ViolationReportSerializer,
)
from squeaky_clean.application.generation.recovery.squib.squib_review_gate import SquibReviewGate
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class RecoveryEmitter:
    """Ingest a Python project and emit a faithful Squib + violation report.

    Runs the deterministic front-half — ingest, layer, classify (no LLM
    tie-break, so the emit is free and reproducible), decompose — then
    writes the faithful Squib (Recover), runs the analyzer suite and writes
    a categorized violations.json + review markdown (Analyze), and computes
    the preserve-vs-split MCDA verdict under the user's criteria ranking. No
    regeneration and no refactoring run — those are downstream phases.
    """

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs
        self._extractors: ClassCatalogExtractorFactory = ClassCatalogExtractorFactory()
        self._layers: LayerAssigner = LayerAssigner()
        self._patterns: PatternClassifier = PatternClassifier()
        self._decomposer: ModuleDecomposer = ModuleDecomposer()
        self._gate: SquibReviewGate = SquibReviewGate(fs)
        self._analysis: ViolationAnalysis = ViolationAnalysis()
        self._serializer: ViolationReportSerializer = ViolationReportSerializer()
        self._renderer: ViolationReportRenderer = ViolationReportRenderer()
        self._weighting: CriteriaWeighting = CriteriaWeighting()
        self._decider: RefactorDecider = RefactorDecider()

    def emit(
        self, root: Path, out_path: Path, ranking: tuple[str, ...],
        language: TargetLanguage = TargetLanguage.PYTHON,
    ) -> RecoverySummary:
        """Emit the Squib + violations report; return a RecoverySummary."""
        catalog = self._extractors.for_language(language).extract(root)
        layers = self._layers.assign(catalog)
        spec = self._decomposer.decompose(
            catalog, layers, self._patterns.classify_all(catalog, layers),
        )
        self._gate.emit(spec, out_path)
        report = self._analysis.analyze(RecoveryArtifact(catalog, layers, spec))
        vpath = out_path.with_name(out_path.name + ".violations.json")
        self._fs.write(vpath, self._serializer.serialize(report))
        self._fs.write(
            out_path.with_name(out_path.name + ".violations.md"),
            self._renderer.render(report),
        )
        outcome = self._decider.decide(self._weighting.from_ranking(ranking))
        return RecoverySummary(
            classes=len(catalog.classes), modules=len(spec.modules),
            violations=len(report.violations),
            coupling_violations=len(report.by_category().get("framework-coupling", ())),
            recommendation=outcome.winner, recommendation_close=outcome.close,
            squib_path=str(out_path), violations_path=str(vpath),
        )
