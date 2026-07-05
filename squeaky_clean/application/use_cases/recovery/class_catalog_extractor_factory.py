"""ClassCatalogExtractorFactory: pick the ingest extractor for a language."""

from squeaky_clean.application.use_cases.recovery.class_catalog_extractor import (
    ClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.java_catalog_extractor import (
    JavaClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.javascript_catalog_extractor import (
    JavaScriptClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.python_class_catalog_extractor import (
    PythonClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.typescript_catalog_extractor import (
    TypeScriptClassCatalogExtractor,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class ClassCatalogExtractorFactory:
    """Resolves a TargetLanguage to its recovery ingest extractor.

    Python uses a true AST walk; Java/JavaScript/TypeScript use regex
    extractors (lower fidelity, documented). Go and Rust have no recovery
    extractor yet and raise — recovery is opt-in per supported language.
    """

    def for_language(self, language: TargetLanguage) -> ClassCatalogExtractor:
        """Return the extractor for ``language`` or raise if unsupported."""
        if language is TargetLanguage.PYTHON:
            return PythonClassCatalogExtractor()
        if language is TargetLanguage.JAVASCRIPT:
            return JavaScriptClassCatalogExtractor()
        if language is TargetLanguage.TYPESCRIPT:
            return TypeScriptClassCatalogExtractor()
        if language is TargetLanguage.JAVA:
            return JavaClassCatalogExtractor()
        raise ValueError(f"recovery ingest not supported for {language.value}")
