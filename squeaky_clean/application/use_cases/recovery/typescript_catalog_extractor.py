"""TypeScriptClassCatalogExtractor: recover a TypeScript project's classes."""

from squeaky_clean.application.use_cases.recovery.ecmascript_catalog_extractor import (
    EcmaScriptCatalogExtractor,
)


class TypeScriptClassCatalogExtractor(EcmaScriptCatalogExtractor):
    """ECMAScript extractor scoped to ``*.ts`` files."""

    _GLOB = "*.ts"
