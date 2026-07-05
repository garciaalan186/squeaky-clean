"""JavaClassCatalogExtractor: recover a Java project's classes."""

import re
from collections.abc import Callable

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.regex_catalog_extractor import (
    RegexCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.regex_class_parser import (
    RegexClassParser,
)

_PACKAGE: re.Pattern[str] = re.compile(r"^\s*package\s+(?P<pkg>[\w.]+)\s*;", re.MULTILINE)
_IMPORT: re.Pattern[str] = re.compile(
    r"^\s*import\s+(?:static\s+)?(?P<imp>[\w.]+)\s*;", re.MULTILINE,
)
_CLASS: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:public\s+|final\s+|abstract\s+)*(?:class|interface|enum)\s+(?P<name>\w+)"
    r"(?:\s+extends\s+(?P<base>[\w.]+))?(?:\s+implements\s+(?P<impl>[\w., ]+))?",
    re.MULTILINE,
)
_METHOD: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:public|protected)\s+(?:static\s+)?(?:final\s+)?"
    r"[\w<>\[\].]+\s+(?P<name>\w+)\s*\((?P<args>[^)]*)\)",
    re.MULTILINE,
)
_FIELD: re.Pattern[str] = re.compile(
    r"^[ \t]*(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?"
    r"(?P<type>[\w<>\[\].]+)\s+(?P<name>\w+)\s*[;=]",
    re.MULTILINE,
)


class JavaClassCatalogExtractor(RegexCatalogExtractor):
    """Extracts classes from Java sources, keyed by their package FQN.

    The ``package`` declaration plus the class name yield a real FQN, so
    ``import com.foo.Bar;`` resolves against catalogued classes and the
    import graph is meaningful (unlike ECMAScript's relative paths).
    Annotations (``@RestController``, ``@Entity``) feed layer detection.
    """

    _GLOB = "*.java"

    def __init__(self) -> None:
        super().__init__()
        self._parser: RegexClassParser = RegexClassParser(_CLASS, _METHOD, _FIELD)

    def _records(self, source: str, prefix: str) -> tuple[ClassRecord, ...]:
        package = _PACKAGE.search(source)
        pkg = package.group("pkg") if package is not None else ""
        imports = tuple(m.group("imp") for m in _IMPORT.finditer(source))
        fqn_of: Callable[[str], str] = (
            (lambda name: f"{pkg}.{name}") if pkg else (lambda name: name)
        )
        return self._parser.parse(source, fqn_of, imports)
