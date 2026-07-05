"""JavaScriptClassCatalogExtractor: recover a JavaScript project's classes."""

from squeaky_clean.application.use_cases.recovery.ecmascript_catalog_extractor import (
    EcmaScriptCatalogExtractor,
)


class JavaScriptClassCatalogExtractor(EcmaScriptCatalogExtractor):
    """ECMAScript extractor scoped to ``*.js`` files."""

    _GLOB = "*.js"
