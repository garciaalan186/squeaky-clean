"""FenceExtractor: shared helper to strip a fenced code block from raw text."""

import re

from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)

_FENCE: re.Pattern[str] = re.compile(
    r"```[A-Za-z0-9_+-]*\s*\n(?P<body>.*?)```", re.DOTALL
)


class FenceExtractor:
    """Extracts the body of the first fenced code block in raw text."""

    def extract(self, raw: str, class_name: str) -> str:
        """Return a fenced code block, preferring the one that defines the class.

        When a response carries several fences (an explanatory snippet plus the
        real class, say), first-match can grab the wrong one. Preference order:
        a fence that *defines* ``class_name`` (definition keyword + name), then
        any fence mentioning it, then the first fence (R3.1).
        """
        bodies = [m.group("body") for m in _FENCE.finditer(raw)]
        if not bodies:
            raise ImplementedClassParseError(
                f"missing fenced code block for {class_name}"
            )
        defn = re.compile(
            r"\b(?:class|struct|interface|type|enum|object|def|fn|func)\s+"
            + re.escape(class_name) + r"\b"
        )
        chosen = (
            next((b for b in bodies if defn.search(b)), None)
            or next((b for b in bodies if class_name in b), None)
            or bodies[0]
        )
        return chosen.strip("\n").rstrip()
