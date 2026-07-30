"""SnakeCaseConverter: CamelCase / PascalCase identifier -> snake_case."""


class SnakeCaseConverter:
    """Converts a PascalCase or camelCase identifier to snake_case."""

    def convert(self, camel: str) -> str:
        """Return the snake_case form of ``camel``.

        Inserts an underscore before each uppercase letter that follows
        either a lowercase letter, a digit, or another uppercase letter
        that is itself followed by a lowercase letter. Lowercases the
        whole string. ``CalculatorService`` -> ``calculator_service`` and
        ``P0Calculator`` -> ``p0_calculator``.
        """
        if not camel:
            return ""
        out: list[str] = []
        for idx, ch in enumerate(camel):
            if ch.isupper() and idx > 0 and self._needs_underscore(camel, idx):
                out.append("_")
            out.append(ch.lower())
        return "".join(out)

    def _needs_underscore(self, camel: str, idx: int) -> bool:
        prev = camel[idx - 1]
        if prev.islower() or prev.isdigit():
            return True
        if idx + 1 < len(camel) and camel[idx + 1].islower():
            return True
        return False
