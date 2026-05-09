"""OriginAllowlist: strict prefix-based URL allowlist for tech-doc fetches."""


class OriginAllowlist:
    """Pure helper: True iff URL starts with any of the allowed prefixes."""

    def __init__(self, allowed_prefixes: tuple[str, ...]) -> None:
        self._allowed: tuple[str, ...] = tuple(allowed_prefixes)

    def is_allowed(self, url: str) -> bool:
        """Return True iff url begins with one of the allowed prefixes."""
        if not self._allowed:
            return False
        return any(url.startswith(prefix) for prefix in self._allowed)
