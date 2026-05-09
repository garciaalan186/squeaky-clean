"""NotationSectionExtractor: pull top-level sections out of §Notation text."""

from squeaky_clean.application.use_cases.notation_brace_scanner import NotationBraceScanner
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


class NotationSectionExtractor:
    """Splits raw §Notation text into labelled top-level sections."""

    def __init__(self) -> None:
        self._scanner: NotationBraceScanner = NotationBraceScanner()

    def extract(self, text: str) -> dict[str, str]:
        """Return dict of section name -> raw body string.

        Tolerates multi-MODULE output: if the same section keyword appears
        more than once (e.g. PA emits two `MODULE` blocks), the first
        occurrence wins for singleton sections (MODULE, LAYER) and later
        `CLASSES`/`EXPORTS`/`DEPENDS`/`INVARIANTS` bodies are appended so
        downstream parsers see the union across blocks.
        """
        cleaned = text.strip()
        if not cleaned:
            raise NotationParseError("empty §Notation input")
        sections: dict[str, str] = {}
        idx = 0
        singletons = {"MODULE", "LAYER"}
        while idx < len(cleaned):
            if cleaned[idx].isspace():
                idx += 1
                continue
            name, idx = self._read_keyword(cleaned, idx)
            body, idx = self._read_body(cleaned, idx)
            if name in sections and name not in singletons:
                sections[name] = sections[name] + "\n" + body
            elif name not in sections:
                sections[name] = body
        return sections

    def _read_keyword(self, text: str, idx: int) -> tuple[str, int]:
        start = idx
        while idx < len(text) and (text[idx].isalpha() or text[idx] == "_"):
            idx += 1
        word = text[start:idx]
        if not word:
            raise NotationParseError(f"expected keyword at position {start}")
        return word, idx

    def _read_body(self, text: str, idx: int) -> tuple[str, int]:
        while idx < len(text) and text[idx] == " ":
            idx += 1
        if idx >= len(text):
            return "", idx
        char = text[idx]
        if char == "[":
            return self._scanner.inside_bracket(text, idx)
        if char == "{":
            return self._scanner.inside_brace(text, idx)
        end = text.find("\n", idx)
        if end == -1:
            return text[idx:].strip(), len(text)
        return text[idx:end].strip(), end
