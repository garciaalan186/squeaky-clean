"""RegexDecoratorScanner: gather annotations around a class declaration."""

import re

_DECORATOR: re.Pattern[str] = re.compile(r"@(\w+)")
_LEADING: re.Pattern[str] = re.compile(r"^@(\w+)")


class RegexDecoratorScanner:
    """Collects class- and method-level annotations for one class.

    Leading annotations are the contiguous ``@Name`` lines directly above
    the class declaration (Java ``@RestController``, TS ``@Controller``);
    body annotations are the ``@Name`` decorators inside the class (method
    routes like ``@GetMapping``). Both feed Stage-2 INTERFACE detection, so
    they are folded into one deduplicated tuple.
    """

    def scan(self, source: str, decl_start: int, body: str) -> tuple[str, ...]:
        """Return the deduplicated annotation names for the class."""
        out: list[str] = list(self._leading(source[:decl_start]))
        out.extend(match.group(1) for match in _DECORATOR.finditer(body))
        return tuple(dict.fromkeys(out))

    def _leading(self, before: str) -> list[str]:
        out: list[str] = []
        for line in reversed(before.splitlines()):
            stripped = line.strip()
            if not stripped:
                break
            match = _LEADING.match(stripped)
            if match is None:
                break
            out.append(match.group(1))
        return out
