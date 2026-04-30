"""tech_doc_sanitizer: deterministic anti-poisoning sanitizer (design §4.6)."""

import json
import re
from typing import cast

_MAX_BYTES: int = 100 * 1024
_MAX_FIELD: int = 5 * 1024
_TAG_RE = re.compile(
    r"<(script|style|iframe)\b[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
_ATTR_RE = re.compile(
    r"\s+on[a-zA-Z]+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)",
    re.IGNORECASE,
)
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore (?:prior|previous|all) instructions", re.IGNORECASE),
    re.compile(r"you are now\b", re.IGNORECASE),
    re.compile(r"forget your\b", re.IGNORECASE),
    re.compile(r"^system:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^assistant:", re.IGNORECASE | re.MULTILINE),
)


class TechDocPoisonedError(RuntimeError):
    """Raised when sanitizer rejects content as unsafe."""


def sanitize(content: str) -> str:
    """Strip dangerous markup; reject on size or prompt-injection markers."""
    if len(content.encode("utf-8")) > _MAX_BYTES:
        raise TechDocPoisonedError("content exceeds 100 KB cap")
    cleaned = _TAG_RE.sub("", content)
    cleaned = _ATTR_RE.sub("", cleaned)
    for pat in _INJECTION_PATTERNS:
        if pat.search(cleaned):
            raise TechDocPoisonedError(
                f"prompt-injection marker matched: {pat.pattern!r}"
            )
    _check_json_field_sizes(cleaned)
    return cleaned


def _check_json_field_sizes(content: str) -> None:
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(parsed, dict):
        return
    parsed_dict = cast(dict[str, object], parsed)
    for key in ("code", "description"):
        value = parsed_dict.get(key)
        if isinstance(value, str) and len(value.encode("utf-8")) > _MAX_FIELD:
            raise TechDocPoisonedError(
                f"JSON field {key!r} exceeds 5 KB"
            )
    ops = parsed_dict.get("primary_operations")
    if isinstance(ops, list):
        for op in cast(list[object], ops):
            if isinstance(op, dict):
                _check_json_field_sizes(json.dumps(op))
