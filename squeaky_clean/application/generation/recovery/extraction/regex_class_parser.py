"""RegexClassParser: slice a source file into ClassRecords via regexes."""

import re
from collections.abc import Callable

from squeaky_clean.application.generation.recovery.extraction.class_grammar import ClassGrammar
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.extraction.regex_decorator_scanner import (
    RegexDecoratorScanner,
)

_KEYWORDS: frozenset[str] = frozenset({
    "if", "for", "while", "switch", "catch", "return", "function",
    "constructor", "super", "new", "await", "typeof",
})


class RegexClassParser:
    """Turns one file's source into ClassRecords using a ClassGrammar.

    Constructed per file: the grammar is the language's declaration
    regexes and ``imports`` is that file's import list, attached to every
    record. Each class body runs from its declaration to the next
    class's. Approximate by design — regex, not a real parser — but
    enough to feed the language-neutral downstream pipeline.
    """

    def __init__(self, grammar: ClassGrammar, imports: tuple[str, ...] = ()) -> None:
        self._grammar: ClassGrammar = grammar
        self._imports: tuple[str, ...] = imports
        self._decorators: RegexDecoratorScanner = RegexDecoratorScanner()

    def parse(
        self, source: str, fqn_of: Callable[[str], str],
    ) -> tuple[ClassRecord, ...]:
        """Return the ClassRecords declared in ``source``."""
        matches = list(self._grammar.class_re.finditer(source))
        out: list[ClassRecord] = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
            body = source[match.end():end]
            out.append(ClassRecord(
                fqn=fqn_of(match.group("name")), bases=self._bases(match),
                methods=self._methods(body), fields=self._fields(body),
                imports=self._imports,
                decorators=self._decorators.scan(source[:match.start()], body),
            ))
        return tuple(out)

    def _bases(self, match: re.Match[str]) -> tuple[str, ...]:
        groups = match.groupdict()
        out: list[str] = []
        if groups.get("base"):
            out.append(groups["base"].strip())
        if groups.get("impl"):
            out.extend(b.strip() for b in groups["impl"].split(",") if b.strip())
        return tuple(out)

    def _methods(self, body: str) -> tuple[str, ...]:
        return tuple(
            f"{m.group('name')}({m.group('args').strip()})"
            for m in self._grammar.method_re.finditer(body)
            if m.group("name") not in _KEYWORDS
        )

    def _fields(self, body: str) -> tuple[str, ...]:
        return tuple(
            f"{m.group('name')}: {m.group('type').strip()}"
            for m in self._grammar.field_re.finditer(body)
        )
