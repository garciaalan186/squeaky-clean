"""WebFetchTechDocFetcher: stdlib-urllib HTTP fetcher with strict caps (H4)."""

from urllib.error import URLError
from urllib.request import Request, urlopen

from squeaky_clean.domain.interfaces.tech_doc_fetcher import (
    TechDocFetcher,
    TechDocFetchError,
)

_MAX_BYTES: int = 100 * 1024
_CHUNK: int = 16 * 1024
_USER_AGENT: str = "squeaky-techspec-fetcher/1.0"
_ALLOWED_TYPES: frozenset[str] = frozenset(
    {"text/html", "text/plain", "application/json"}
)


class WebFetchTechDocFetcher(TechDocFetcher):
    """urllib-based fetcher with timeout, size cap, content-type whitelist."""

    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout: float = float(timeout_seconds)

    def fetch(self, url: str) -> str:
        """Return decoded body or raise TechDocFetchError."""
        req = Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            with urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                self._check_content_type(resp.headers.get("Content-Type", ""))
                return self._read_capped(resp)
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise TechDocFetchError(f"fetch failed for {url}: {exc}") from exc

    @staticmethod
    def _check_content_type(header: str) -> None:
        ctype = header.split(";", 1)[0].strip().lower()
        if ctype not in _ALLOWED_TYPES:
            raise TechDocFetchError(f"disallowed content-type: {ctype!r}")

    @staticmethod
    def _read_capped(resp: object) -> str:
        chunks: list[bytes] = []
        size = 0
        read = getattr(resp, "read", None)
        if read is None:
            raise TechDocFetchError("response has no read()")
        while True:
            chunk = read(_CHUNK)
            if not chunk:
                break
            size += len(chunk)
            if size > _MAX_BYTES:
                raise TechDocFetchError(
                    f"body exceeds {_MAX_BYTES} bytes"
                )
            chunks.append(chunk)
        return b"".join(chunks).decode("utf-8", errors="replace")
