"""NotationBraceScanner: find the inner text of a balanced {...} or [...]."""

from squeaky_clean.application.use_cases.notation_scan_target import NotationScanTarget
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


class NotationBraceScanner:
    """Scans a string for a balanced `{...}` or `[...]` region."""

    def inside_brace(self, text: str, idx: int) -> tuple[str, int]:
        """Return (inner, end_idx) for a balanced `{...}` starting at idx."""
        return self._scan(NotationScanTarget(text, "{", "}"), idx)

    def inside_bracket(self, text: str, idx: int) -> tuple[str, int]:
        """Return (inner, end_idx) for a balanced `[...]` starting at idx."""
        return self._scan(NotationScanTarget(text, "[", "]"), idx)

    def _scan(
        self, target: NotationScanTarget, idx: int
    ) -> tuple[str, int]:
        text = target.text
        if idx >= len(text) or text[idx] != target.opener:
            raise NotationParseError(
                f"expected {target.opener} at position {idx}"
            )
        depth = 0
        start = idx
        while idx < len(text):
            ch = text[idx]
            if ch == target.opener:
                depth += 1
            elif ch == target.closer:
                depth -= 1
                if depth == 0:
                    return text[start + 1 : idx].strip(), idx + 1
            idx += 1
        raise NotationParseError(
            f"unbalanced {target.opener}{target.closer}"
        )
