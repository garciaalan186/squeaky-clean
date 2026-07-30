"""atomic_write_text: crash-safe file replacement via tmp + os.replace.

A bare ``Path.write_text`` truncates the target before writing, so a crash
(including a budget-exit kill) mid-write leaves a half-written file that a
later resume parses as corrupt. Writing to a sibling temp file and atomically
renaming it guarantees a reader sees either the old contents or the new ones,
never a partial. Extracted from ``CheckpointWriter`` (the one site that already
did this) for reuse across every framework-internal result artifact.
"""

from __future__ import annotations

import os
from pathlib import Path


def atomic_write_text(path: Path, content: str) -> None:
    """Write ``content`` to ``path`` atomically, creating parents as needed.

    The temp file lives in the target directory so ``os.replace`` stays on one
    filesystem (a cross-device rename would raise). On success the target is
    replaced in a single atomic step; on failure the temp file is removed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(content)
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)
        raise
