"""ImplementedClassParser port: extract a class body from raw ICP output."""

from abc import ABC, abstractmethod


class ImplementedClassParser(ABC):
    """Port for parsing a fenced ICP response into source for a named class."""

    @abstractmethod
    def parse(self, raw_response: str, class_name: str) -> str:
        """Extract the implementation body declaring ``class_name``.

        Raises ``ImplementedClassParseError`` on failure.
        """
