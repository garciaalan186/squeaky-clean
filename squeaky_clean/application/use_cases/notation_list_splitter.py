"""NotationListSplitter: split §Notation bracketed list bodies."""


class NotationListSplitter:
    """Splits the body of a §Notation `[...]` list into tuple items."""

    def plain_tuple(self, raw: str) -> tuple[str, ...]:
        """Split a bracketed list, honoring commas inside `<...>` groups."""
        stripped = raw.strip().strip("[]").strip()
        if not stripped:
            return ()
        return tuple(self._split_top_commas(stripped))

    def method_tuple(self, raw: str) -> tuple[str, ...]:
        """Split a method list, honoring commas inside `(...)` and `<...>`."""
        stripped = raw.strip().strip("[]").strip()
        if not stripped:
            return ()
        return tuple(self._split_top_commas(stripped))

    def _split_top_commas(self, text: str) -> list[str]:
        parts: list[str] = []
        depth = 0
        start = 0
        for i, ch in enumerate(text):
            if ch in ("(", "<", "["):
                depth += 1
            elif ch in (")", ">", "]"):
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(text[start:i].strip())
                start = i + 1
        parts.append(text[start:].strip())
        return [p for p in parts if p]
