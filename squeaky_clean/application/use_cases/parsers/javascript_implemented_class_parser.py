"""JavaScriptImplementedClassParser: detects JS/TS class & function declarations."""

import re

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.fence_extractor import FenceExtractor
from squeaky_clean.domain.interfaces.implemented_class_parser import ImplementedClassParser

_PREFIX: str = r"(?:export\s+(?:default\s+)?)?(?:abstract\s+)?"
_KIND: str = r"(?:class|interface|function|type|enum)"


class JavaScriptImplementedClassParser(ImplementedClassParser):
    """Parser for JavaScript and TypeScript class-like declarations."""

    def __init__(self) -> None:
        self._extractor: FenceExtractor = FenceExtractor()

    def parse(self, raw_response: str, class_name: str) -> str:
        """Return the body declaring ``class_name`` or raise."""
        body = self._extractor.extract(raw_response, class_name)
        pattern = re.compile(
            rf"(?m)^\s*{_PREFIX}{_KIND}\s+{re.escape(class_name)}\b"
        )
        if pattern.search(body) is None:
            raise ImplementedClassParseError(
                f"code body does not declare class {class_name}"
            )
        return body
