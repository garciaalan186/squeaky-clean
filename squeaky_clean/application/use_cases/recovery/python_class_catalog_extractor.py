"""PythonClassCatalogExtractor: Stage-1 ingest of a Python brownfield repo."""

import ast
from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.import_graph_resolver import (
    ImportGraphResolver,
)
from squeaky_clean.application.use_cases.recovery.ingest_scope import IngestScope
from squeaky_clean.application.use_cases.recovery.python_class_extractor import (
    PythonClassExtractor,
)


class PythonClassCatalogExtractor:
    """Walks a Python source tree and produces a deterministic ClassCatalog.

    Every ``*.py`` file under the root is parsed; its top-level classes
    become ClassRecords keyed by an FQN derived from the file's path
    relative to the root (``__init__`` segments dropped). Test code and
    vendored/build directories are excluded by IngestScope, so the catalog
    reflects the project's own production code. Files that fail to parse
    are skipped deterministically. The class-level import graph is resolved
    against the catalogued FQNs. No LLM runs — the same tree yields the same
    catalog on every run.
    """

    def __init__(self) -> None:
        self._extractor: PythonClassExtractor = PythonClassExtractor()
        self._resolver: ImportGraphResolver = ImportGraphResolver()
        self._scope: IngestScope = IngestScope()

    def extract(self, root: Path) -> ClassCatalog:
        """Return the ClassCatalog for every class under ``root``."""
        records: list[ClassRecord] = []
        for path in sorted(root.rglob("*.py")):
            if self._scope.includes(path, root):
                records.extend(self._records_for(path, root))
        frozen = tuple(records)
        return ClassCatalog(classes=frozen, import_graph=self._resolver.resolve(frozen))

    def _records_for(self, path: Path, root: Path) -> tuple[ClassRecord, ...]:
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, UnicodeDecodeError):
            return ()
        return self._extractor.extract(tree, self._prefix(path, root))

    def _prefix(self, path: Path, root: Path) -> str:
        parts = list(path.relative_to(root).with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts)
