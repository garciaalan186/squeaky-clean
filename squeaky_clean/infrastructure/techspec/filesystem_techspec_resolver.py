"""FilesystemTechSpecResolver: bundled-snapshot + cache resolver (H1)."""

import json
import logging
from pathlib import Path
from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.interfaces.tech_spec_resolver import (
    TechSpecResolver,
    TechSpecUnresolvableError,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder

_LOG = logging.getLogger(__name__)


class FilesystemTechSpecResolver(TechSpecResolver):
    """Resolves TechSpecs from bundled snapshots, falling back to local cache."""

    def __init__(
        self, root: Path, validator: TechSpecValidator,
    ) -> None:
        self._root: Path = root
        self._validator: TechSpecValidator = validator
        self._builder: TechSpecBuilder = TechSpecBuilder()

    def resolve(
        self, category: str, technology: str, version: str,
    ) -> TechSpec:
        """Return TechSpec for the triple or raise TechSpecUnresolvableError."""
        for candidate in self._candidate_paths(category, technology, version):
            spec = self._try_load(candidate)
            if spec is not None:
                return spec
        raise TechSpecUnresolvableError(
            f"no TechSpec for ({category}, {technology}, {version}) "
            f"under {self._root}"
        )

    def _candidate_paths(
        self, category: str, technology: str, version: str,
    ) -> tuple[Path, ...]:
        return (
            self._root / category / technology / f"{version}.json",
            self._root / ".cache" / category / technology / f"{version}.json",
        )

    def _try_load(self, path: Path) -> TechSpec | None:
        if not path.is_file():
            return None
        try:
            raw = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            _LOG.warning("techspec unreadable at %s: %s", path, exc)
            return None
        if not isinstance(raw, dict):
            _LOG.warning("techspec at %s is not a JSON object", path)
            return None
        candidate = cast(dict[str, object], raw)
        violations = self._validator.validate(candidate)
        if violations:
            _LOG.warning("techspec at %s invalid: %s", path, violations)
            return None
        try:
            return self._builder.build(candidate)
        except (ValueError, TypeError) as exc:
            _LOG.warning("techspec at %s rejected: %s", path, exc)
            return None
