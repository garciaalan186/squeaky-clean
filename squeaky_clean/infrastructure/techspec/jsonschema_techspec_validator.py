"""JSONSchemaTechSpecValidator: jsonschema-backed TechSpecValidator adapter."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator


class JSONSchemaTechSpecValidator(TechSpecValidator):
    """Loads the v1 schema once and runs Draft-2020-12 validation per call."""

    def __init__(self, schema_path: Path) -> None:
        self._schema_path: Path = schema_path
        self._validator: Draft202012Validator = Draft202012Validator(
            json.loads(schema_path.read_text())
        )

    def validate(self, candidate: dict[str, object]) -> tuple[str, ...]:
        """Return tuple of violation messages (empty = valid)."""
        return tuple(
            f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: "
            f"{err.message}"
            for err in self._validator.iter_errors(candidate)
        )
