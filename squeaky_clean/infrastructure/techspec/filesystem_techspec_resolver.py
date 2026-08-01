"""FilesystemTechSpecResolver: bundled-snapshot + cache resolver (H1).

R6.8: rejected snapshots are logged (``techspec_snapshot_rejected``) and the
reasons travel into ``TechSpecResolutionError``; a missing file stays silent.
"""

import json
from pathlib import Path
from typing import cast

from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.interfaces.tech_spec_resolver import (
    TechSpecResolutionError,
    TechSpecResolver,
)
from squeaky_clean.domain.interfaces.tech_spec_validator import TechSpecValidator
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder


class FilesystemTechSpecResolver(TechSpecResolver):
    """Resolves TechSpecs from bundled snapshots, falling back to local cache."""

    def __init__(
        self, root: Path, validator: TechSpecValidator,
        *, run_logger: RunLogger | None = None,
    ) -> None:
        self._root: Path = root
        self._validator: TechSpecValidator = validator
        self._builder: TechSpecBuilder = TechSpecBuilder()
        self._log: RunLogger = run_logger or NullRunLogger()

    def resolve(self, target: TechSpecTarget) -> TechSpec:
        """Return TechSpec for the target or raise TechSpecResolutionError."""
        reasons: list[str] = []
        for candidate in self._candidate_paths(target):
            loaded = self._try_load(candidate)
            if isinstance(loaded, TechSpec):
                return loaded
            if loaded is not None:
                self._log.event(
                    "techspec_snapshot_rejected",
                    path=str(candidate), reason=loaded.reason,
                )
                reasons.append(f"{candidate}: {loaded.reason}")
        raise TechSpecResolutionError(
            f"no TechSpec for ({target.category}, {target.technology}, "
            f"{target.version_pin}) under {self._root}",
            tuple(reasons),
        )

    def _candidate_paths(self, target: TechSpecTarget) -> tuple[Path, ...]:
        category, technology = target.category, target.technology
        version = target.version_pin
        return (
            self._root / category / technology / f"{version}.json",
            self._root / ".cache" / category / technology / f"{version}.json",
        )

    def _try_load(self, path: Path) -> TechSpec | TechSpecFetchFailed | None:
        """Load one snapshot; None = file absent, failures carry a reason."""
        if not path.is_file():
            return None
        try:
            raw = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            return TechSpecFetchFailed(f"unreadable: {exc}")
        if not isinstance(raw, dict):
            return TechSpecFetchFailed("not a JSON object")
        candidate = cast(dict[str, object], raw)
        violations = self._validator.validate(candidate)
        if violations:
            return TechSpecFetchFailed(f"invalid: {violations}")
        try:
            return self._builder.build(candidate)
        except (ValueError, TypeError) as exc:
            return TechSpecFetchFailed(f"rejected by builder: {exc}")
