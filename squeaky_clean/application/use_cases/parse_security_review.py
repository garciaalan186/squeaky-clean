"""ParseSecurityReview: decode SecurityArchitect LLM output into a SecurityReview."""

import re

from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.dtos.security_review import SecurityReview

_SECTION = re.compile(
    r"SECURITY_REVIEW\s*\n-{3,}\s*\n(?P<body>.*?)\n-{3,}",
    re.DOTALL,
)
_CONCERN = re.compile(
    r"CONCERN\s+(?P<cat>\S+)\s+(?P<cls>\S+)\s*\n"
    r"DESCRIPTION\s+(?P<desc>.+)\n"
    r"TEST\s+(?P<test>.+)",
)


class ParseSecurityReview:
    """Parses the SecurityArchitect output format into a SecurityReview DTO."""

    def parse(self, raw: str) -> SecurityReview:
        """Return a SecurityReview built from SecurityArchitect raw output."""
        match = _SECTION.search(raw)
        if match is None:
            return SecurityReview(concerns=())
        body = match.group("body")
        concerns: list[SecurityConcern] = []
        for block in _CONCERN.finditer(body):
            concerns.append(
                SecurityConcern(
                    category=block.group("cat").strip(),
                    target_class=block.group("cls").strip(),
                    description=block.group("desc").strip(),
                    test_scenario=block.group("test").strip(),
                )
            )
        return SecurityReview(concerns=tuple(concerns))
