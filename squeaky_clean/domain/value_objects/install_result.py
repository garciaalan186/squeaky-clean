"""InstallResult DTO: outcome of a DependencyInstaller.install() call."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstallResult:
    """Frozen result of a dependency install attempt.

    ``succeeded`` is True iff the package manager exited 0; ``message``
    captures a short human-readable status (truncated logs on failure,
    "ok" / "skipped" on success). ``duration_ms`` is the wall-clock
    duration of the install subprocess in milliseconds.
    """

    succeeded: bool
    duration_ms: int
    message: str
