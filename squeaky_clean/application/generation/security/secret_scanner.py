"""SecretScanner: detect API keys / credentials in generated content."""

from __future__ import annotations

import re

_PATTERNS: tuple[tuple[str, str], ...] = (
    ("anthropic_api_key", r"sk-ant-[A-Za-z0-9_-]{20,}"),
    ("openai_api_key", r"sk-[A-Za-z0-9]{20,}"),
    ("aws_access_key", r"AKIA[0-9A-Z]{16}"),
    ("aws_session_key", r"ASIA[0-9A-Z]{16}"),
    ("github_token", r"gh[pousr]_[A-Za-z0-9]{20,}"),
    ("slack_token", r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    ("private_key_block", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("password_assignment", r"(?i)password\s*=\s*[\"'][^\"']{4,}[\"']"),
    ("anthropic_env_assignment", r"(?i)ANTHROPIC_API_KEY\s*=\s*sk-ant-"),
    ("openai_env_assignment", r"(?i)OPENAI_API_KEY\s*=\s*sk-"),
)

_BLOCKED_FILENAMES: frozenset[str] = frozenset({
    ".env", ".envrc", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa",
})

_BLOCKED_SUFFIXES: tuple[str, ...] = (".pem", ".key")


class SecretScanner:
    """Pure-function scanner that returns matched secret labels."""

    def scan(self, text: str) -> tuple[str, ...]:
        """Return tuple of matched secret labels (empty if clean)."""
        hits: list[str] = []
        for label, pattern in _PATTERNS:
            if re.search(pattern, text):
                hits.append(label)
        return tuple(hits)

    def filename_blocked(self, filename: str) -> str | None:
        """Return a label if ``filename`` (basename) is on the blocklist."""
        if filename in _BLOCKED_FILENAMES:
            return f"blocked_filename:{filename}"
        for suffix in _BLOCKED_SUFFIXES:
            if filename.endswith(suffix):
                return f"blocked_suffix:{suffix}"
        return None
