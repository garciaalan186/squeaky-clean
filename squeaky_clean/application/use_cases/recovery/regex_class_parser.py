"""RegexClassParser: slice a source file into ClassRecords via regexes."""

import re
from collections.abc import Callable

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.regex_decorator_scanner import (
    RegexDecoratorScanner,
)

_KEYWORDS: frozenset[str] = frozenset({
    "if", "for", "while", "switch", "catch", "return", "function",
    "constructor", "super", "new", "await", "typeof",
})


class RegexClassParser:
    """Turns one file's source into ClassRecords using configured regexes.

    Classes are located by ``class_re`` (named groups ``name``/``base``/
    ``impl``); each class body runs from its declaration to the next
    class's, and methods/fields are matched within it. Approximate by
    design — regex, not a real parser — but enough to feed the
    language-neutral downstream pipeline.
    """

    def __init__(
        self, class_re: re.Pattern[str], method_re: re.Pattern[str],
        field_re: re.Pattern[str],
    ) -> None:
        self._class = class_re
        self._method = method_re
        self._field = field_re
        self._decorators: RegexDecoratorScanner = RegexDecoratorScanner()

    def parse(
        self, source: str, fqn_of: Callable[[str], str], imports: tuple[str, ...],
    ) -> tuple[ClassRecord, ...]:
        """Return the ClassRecords declared in ``source``."""
        matches = list(self._class.finditer(source))
        out: list[ClassRecord] = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
            body = source[match.end():end]
            out.append(ClassRecord(
                fqn=fqn_of(match.group("name")), bases=self._bases(match),
                methods=self._methods(body), fields=self._fields(body),
                imports=imports,
                decorators=self._decorators.scan(source, match.start(), body),
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
            for m in self._method.finditer(body)
            if m.group("name") not in _KEYWORDS
        )

    def _fields(self, body: str) -> tuple[str, ...]:
        return tuple(
            f"{m.group('name')}: {m.group('type').strip()}"
            for m in self._field.finditer(body)
        )
