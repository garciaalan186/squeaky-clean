"""FenceExtractor: shared helper to strip a fenced code block from raw text."""

import re

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)

_FENCE: re.Pattern[str] = re.compile(
    r"```[A-Za-z0-9_+-]*\s*\n(?P<body>.*?)```", re.DOTALL
)


class FenceExtractor:
    """Extracts the body of the first fenced code block in raw text."""

    def extract(self, raw: str, class_name: str) -> str:
        """Return the inner body of the first fence, or raise on failure."""
        match = _FENCE.search(raw)
        if match is None:
            raise ImplementedClassParseError(
                f"missing fenced code block for {class_name}"
            )
        return match.group("body").strip("\n").rstrip()
