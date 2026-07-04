"""ClassCatalog DTO: the full deterministic ingest of a brownfield repo."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord


@dataclass(frozen=True)
class ClassCatalog:
    """Stage-1 output: every class found plus a class-level import graph.

    `classes` holds one ClassRecord per class discovered across all source
    files. `import_graph` maps each class FQN to the FQNs of sibling
    project classes it depends on (edges are resolved to catalog members
    only; stdlib/third-party imports are dropped). Both fields are derived
    without any LLM call, so the same repo yields the same catalog every
    run — the reproducible front-half of Architecture Recovery.
    """

    classes: tuple[ClassRecord, ...]
    import_graph: dict[str, tuple[str, ...]]
