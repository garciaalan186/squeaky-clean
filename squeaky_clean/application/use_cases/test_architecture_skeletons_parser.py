"""TestArchitectureSkeletonsParser: extract TestSkeleton records from raw output."""

import re

from squeaky_clean.application.dtos.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton

_SECTION = re.compile(
    r"TEST_SKELETONS\s*\n-{3,}\s*\n(?P<body>.*)",
    re.DOTALL,
)
_BLOCK = re.compile(
    r"FILE\s+(?P<path>\S+)\s*\nCLASS\s+(?P<cls>\S+)\s*\n"
    r"```[A-Za-z0-9_+-]*\s*\n(?P<code>.*?)```",
    re.DOTALL,
)


class TestArchitectureSkeletonsParser:
    """Extracts TestSkeleton entries from the TEST_SKELETONS section."""

    def parse(self, raw: str) -> tuple[TestSkeleton, ...]:
        """Return a tuple of TestSkeleton records found in the raw output."""
        match = _SECTION.search(raw)
        if match is None:
            return ()
        body = match.group("body")
        skeletons: list[TestSkeleton] = []
        for block in _BLOCK.finditer(body):
            code = block.group("code").strip() + "\n"
            if not code.strip():
                raise TestArchitectureParseError(
                    f"empty code block for class {block.group('cls')}"
                )
            skeletons.append(
                TestSkeleton(
                    class_name=block.group("cls").strip(),
                    file_path=block.group("path").strip(),
                    code=code,
                )
            )
        return tuple(skeletons)
