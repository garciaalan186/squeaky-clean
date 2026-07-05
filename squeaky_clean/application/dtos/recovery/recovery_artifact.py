"""RecoveryArtifact DTO: the faithful, re-analyzable output of recovery."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


@dataclass(frozen=True)
class RecoveryArtifact:
    """A true photograph of the recovered project — the Analyze-phase input.

    Bundles the deterministic ingest (`catalog`), the layer assignment
    (`layers`), and the decomposed `spec`. Recovery persists this faithfully
    — coupling, cycles, and god-classes included — so it can be re-analyzed
    later with better rules and verified against the original source. No
    opinion about what is wrong lives here; that is the Analyze phase's job.
    """

    catalog: ClassCatalog
    layers: dict[str, LayerType]
    spec: ArchitectureSpec
