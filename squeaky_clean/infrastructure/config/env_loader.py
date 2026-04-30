"""EnvLoader: read API key from a .env file without exposing the value."""

from __future__ import annotations

import os
from pathlib import Path


class EnvLoader:
    """Load env vars from a .env file. Caller addresses os.environ to read values.

    Never returns the secret directly through this class's API; callers
    that need the key request it from os.environ. This avoids accidentally
    logging or echoing the value through tooling that captures return values.
    """

    def __init__(self, env_path: Path) -> None:
        self._path: Path = env_path

    def load(self) -> int:
        """Populate os.environ from the .env file. Return number of vars set."""
        if not self._path.exists():
            return 0
        count = 0
        for raw in self._path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                count += 1
        return count
