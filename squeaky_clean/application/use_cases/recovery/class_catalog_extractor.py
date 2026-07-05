"""ClassCatalogExtractor port: ingest a source tree into a ClassCatalog."""

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog


class ClassCatalogExtractor(ABC):
    """Port for the deterministic ingest of one language's source tree.

    Each language implements ``extract`` to walk a project and produce a
    ClassCatalog. Everything downstream — layer assignment, pattern
    classification, decomposition, violation analysis, refactoring — is
    language-neutral, so a new language needs only a new extractor here.
    """

    @abstractmethod
    def extract(self, root: Path) -> ClassCatalog:
        """Return the ClassCatalog for the project rooted at ``root``."""
