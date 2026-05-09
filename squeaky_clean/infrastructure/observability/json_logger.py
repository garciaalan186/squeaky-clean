"""JSONLogger: emit structured one-line JSON events to stdout."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Mapping
from typing import IO


class JSONLogger:
    """Lightweight structured logger; one JSON object per line."""

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream: IO[str] = stream or sys.stdout

    def event(self, kind: str, **fields: object) -> None:
        """Emit a structured event with `kind` plus arbitrary keyword fields."""
        payload: dict[str, object] = {
            "ts": time.time(),
            "kind": kind,
        }
        payload.update(self._coerce(fields))
        line = json.dumps(payload, default=str)
        self._stream.write(line + "\n")
        self._stream.flush()

    def _coerce(self, fields: Mapping[str, object]) -> dict[str, object]:
        return {k: v for k, v in fields.items() if v is not None}
