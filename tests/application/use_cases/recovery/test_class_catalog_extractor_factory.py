"""Tests for ClassCatalogExtractorFactory."""

import pytest

from squeaky_clean.application.use_cases.recovery.class_catalog_extractor_factory import (
    ClassCatalogExtractorFactory,
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


def _for(language: TargetLanguage) -> object:
    return ClassCatalogExtractorFactory().for_language(language)


def test_resolves_each_supported_language() -> None:
    assert isinstance(_for(TargetLanguage.PYTHON), PythonClassCatalogExtractor)
    assert isinstance(_for(TargetLanguage.JAVASCRIPT), JavaScriptClassCatalogExtractor)
    assert isinstance(_for(TargetLanguage.TYPESCRIPT), TypeScriptClassCatalogExtractor)
    assert isinstance(_for(TargetLanguage.JAVA), JavaClassCatalogExtractor)


def test_unsupported_language_raises() -> None:
    with pytest.raises(ValueError):
        _for(TargetLanguage.GO)
    with pytest.raises(ValueError):
        _for(TargetLanguage.RUST)
