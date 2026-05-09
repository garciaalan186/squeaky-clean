"""NotationParseError: raised by ParseNotation on malformed §Notation input."""


class NotationParseError(ValueError):
    """Raised when a §Notation document cannot be parsed into a ModuleSpec."""
