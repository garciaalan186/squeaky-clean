"""NotationFieldParser: parse `key: value, ...` bodies from class entries."""

from squeaky_clean.application.use_cases.notation_brace_scanner import NotationBraceScanner


class NotationFieldParser:
    """Parses the body of a §Notation class entry into a dict of raw values."""

    def __init__(self) -> None:
        self._scanner: NotationBraceScanner = NotationBraceScanner()

    def parse(self, body: str) -> dict[str, str]:
        """Return map of field key -> raw string value for a class body."""
        fields: dict[str, str] = {}
        idx = 0
        while idx < len(body):
            while idx < len(body) and (body[idx].isspace() or body[idx] == ","):
                idx += 1
            if idx >= len(body):
                break
            colon = body.find(":", idx)
            if colon == -1:
                break
            key = body[idx:colon].strip()
            idx = colon + 1
            while idx < len(body) and body[idx] == " ":
                idx += 1
            value, idx = self._read_value(body, idx)
            fields[key] = value.strip()
        return fields

    def _read_value(self, body: str, idx: int) -> tuple[str, int]:
        if idx < len(body) and body[idx] == "[":
            return self._scanner.inside_bracket(body, idx)
        end = idx
        while end < len(body) and body[end] not in ",\n":
            end += 1
        return body[idx:end], end
