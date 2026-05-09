"""NotationInvariantsParser: split the INVARIANTS body into raw strings."""


class NotationInvariantsParser:
    """Parses the inside of an `INVARIANTS [...]` body into a tuple."""

    def parse(self, body: str) -> tuple[str, ...]:
        """Return tuple of invariant strings, stripping wrapping quotes."""
        stripped = body.strip().strip("[]").strip()
        if not stripped:
            return ()
        items: list[str] = []
        depth = 0
        buf: list[str] = []
        in_string = False
        for ch in stripped:
            if ch == '"' and not in_string:
                in_string = True
                continue
            if ch == '"' and in_string:
                in_string = False
                items.append("".join(buf).strip())
                buf.clear()
                continue
            if in_string:
                buf.append(ch)
                continue
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
        return tuple(items)
