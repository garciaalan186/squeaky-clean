"""TestArchitectureParseError: raised when TestArchitect output is unparseable."""


class TestArchitectureParseError(ValueError):
    """Raised when ParseTestArchitecture cannot decode the LLM output."""
