"""ParseImplementedClass: polymorphic entrypoint delegating to a language parser."""

from squeaky_clean.application.use_cases.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)
from squeaky_clean.domain.interfaces.implemented_class_parser import ImplementedClassParser


class ParseImplementedClass:
    """Delegates parsing of an ICP fenced response to a language adapter."""

    def __init__(self, parser: ImplementedClassParser | None = None) -> None:
        self._parser: ImplementedClassParser = parser or PythonImplementedClassParser()

    def parse(self, raw: str, class_name: str) -> str:
        """Extract the implementation body declaring ``class_name``."""
        return self._parser.parse(raw, class_name)
