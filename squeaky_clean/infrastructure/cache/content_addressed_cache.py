"""ContentAddressedCache: sharded on-disk store keyed by content hash."""

from pathlib import Path


class ContentAddressedCache:
    """A simple content-addressed disk cache for LLM replay stability.

    Values are stored under ``<root>/<key[:2]>/<key>.txt`` so a directory
    never accumulates too many entries. Keys are expected to be stable
    content hashes (e.g. ``LLMRequest.cache_key()``). A hit replays the
    exact prior response, giving Architecture Recovery reproducible
    tie-break results across runs of the same project.
    """

    def __init__(self, root: Path) -> None:
        self._root: Path = root

    def get(self, key: str) -> str | None:
        """Return the cached value for ``key``, or None on a miss."""
        path = self._path(key)
        return path.read_text() if path.exists() else None

    def put(self, key: str, value: str) -> None:
        """Store ``value`` under ``key``, creating shards as needed."""
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def _path(self, key: str) -> Path:
        return self._root / key[:2] / f"{key}.txt"
