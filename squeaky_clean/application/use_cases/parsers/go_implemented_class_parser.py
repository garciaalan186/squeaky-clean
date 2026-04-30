"""GoImplementedClassParser: detects Go top-level type declarations."""

import re

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.fence_extractor import FenceExtractor
from squeaky_clean.domain.interfaces.implemented_class_parser import ImplementedClassParser

_GO_TYPE: str = r"type\s+{name}\b\s*(?:struct\b|interface\b|=|[A-Za-z_\[])"


class GoImplementedClassParser(ImplementedClassParser):
    """Parser for Go: ``type Name struct``, ``type Name interface``, aliases."""

    def __init__(self) -> None:
        self._extractor: FenceExtractor = FenceExtractor()

    def parse(self, raw_response: str, class_name: str) -> str:
        """Return the body declaring ``class_name`` or raise."""
        body = self._extractor.extract(raw_response, class_name)
        pattern = re.compile(
            rf"(?m)^\s*{_GO_TYPE.format(name=re.escape(class_name))}"
        )
        if pattern.search(body) is None:
            raise ImplementedClassParseError(
                f"code body does not declare class {class_name}"
            )
        return body
