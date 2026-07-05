"""RegexCatalogExtractor: shared walk/resolve scaffold for regex languages."""

from abc import abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.class_catalog_extractor import (
    ClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.import_graph_resolver import (
    ImportGraphResolver,
)
from squeaky_clean.application.use_cases.recovery.ingest_scope import IngestScope


class RegexCatalogExtractor(ClassCatalogExtractor):
    """Base for regex-based extractors (Java/JS/TS) — no true AST.

    Handles the language-neutral scaffold: walk the tree (honoring
    IngestScope), read each matching file, delegate class extraction to the
    subclass, and resolve the import graph. Subclasses provide the file
    glob and the per-file ``_records`` regex extraction. Fidelity is lower
    than Python's AST path — a documented trade-off for non-Python ingest.
    """

    _GLOB: str = "*"

    def __init__(self) -> None:
        self._scope: IngestScope = IngestScope()
        self._resolver: ImportGraphResolver = ImportGraphResolver()

    def extract(self, root: Path) -> ClassCatalog:
        """Return the ClassCatalog for the project rooted at ``root``."""
        records: list[ClassRecord] = []
        for path in sorted(root.rglob(self._GLOB)):
            if self._scope.includes(path, root):
                records.extend(self._read(path, root))
        frozen = tuple(records)
        return ClassCatalog(classes=frozen, import_graph=self._resolver.resolve(frozen))

    def _read(self, path: Path, root: Path) -> tuple[ClassRecord, ...]:
        try:
            source = path.read_text()
        except (OSError, UnicodeDecodeError):
            return ()
        return self._records(source, self._path_prefix(path, root))

    def _path_prefix(self, path: Path, root: Path) -> str:
        return ".".join(path.relative_to(root).with_suffix("").parts)

    @abstractmethod
    def _records(self, source: str, prefix: str) -> tuple[ClassRecord, ...]:
        """Return ClassRecords parsed from one file's source."""
