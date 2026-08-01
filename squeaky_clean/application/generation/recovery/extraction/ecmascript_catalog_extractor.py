"""EcmaScriptCatalogExtractor: shared JS/TS regex catalog extraction."""

import re

from squeaky_clean.application.generation.recovery.extraction.class_grammar import ClassGrammar
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.extraction.regex_catalog_extractor import (
    RegexCatalogExtractor,
)
from squeaky_clean.application.generation.recovery.extraction.regex_class_parser import (
    RegexClassParser,
)

_CLASS: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:export\s+(?:default\s+)?)?(?:abstract\s+)?class\s+(?P<name>\w+)"
    r"(?:\s+extends\s+(?P<base>[\w.]+))?(?:\s+implements\s+(?P<impl>[\w., ]+))?",
    re.MULTILINE,
)
_METHOD: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|get\s+|set\s+)*"
    r"(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*[:{]",
    re.MULTILINE,
)
_FIELD: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:public\s+|private\s+|protected\s+|readonly\s+)*"
    r"(?P<name>\w+)\s*:\s*(?P<type>[\w<>\[\]| .]+?)\s*[;=]",
    re.MULTILINE,
)
_IMPORT: re.Pattern[str] = re.compile(r"""import\s+(?:[^'"]*from\s+)?['"](?P<mod>[^'"]+)['"]""")
_GRAMMAR = ClassGrammar(class_re=_CLASS, method_re=_METHOD, field_re=_FIELD)


class EcmaScriptCatalogExtractor(RegexCatalogExtractor):
    """Extracts classes from ECMAScript sources (JavaScript and TypeScript).

    Handles ``export``/``abstract`` class forms, ``extends``/``implements``
    bases, method and TS property declarations, and ``@decorator`` metadata.
    FQNs are path-derived; imports are the raw module specifiers (relative
    ECMAScript paths rarely resolve to catalogued FQNs, so the import graph
    is sparser than Python's — a documented regex-fidelity trade-off).
    """

    def _records(self, source: str, prefix: str) -> tuple[ClassRecord, ...]:
        imports = tuple(m.group("mod") for m in _IMPORT.finditer(source))
        return RegexClassParser(_GRAMMAR, imports).parse(
            source, lambda name: f"{prefix}.{name}",
        )
