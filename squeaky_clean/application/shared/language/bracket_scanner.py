"""Bracket-aware lexical scanning helpers for brace-delimited source text.

Pure functions shared by the deterministic TS/JS rewriters: they track
bracket nesting depth so splits and searches ignore separators inside
nested ``()[]{}<>`` groups.
"""

from __future__ import annotations

_OPEN = "([{<"
_CLOSE = ")]}>"


def match_brace(text: str, pos: int) -> int:
    """Index of the ``}`` closing the ``{`` at/after ``pos``; -1 if none."""
    depth = 0
    for i in range(pos, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_top(s: str, sep: str) -> list[str]:
    """Split ``s`` on ``sep`` occurrences at bracket depth 0."""
    parts: list[str] = []
    depth = 0
    last = 0
    for i, ch in enumerate(s):
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(0, depth - 1)
        elif ch == sep and depth == 0:
            parts.append(s[last:i])
            last = i + 1
    parts.append(s[last:])
    return parts


def top_index(s: str, target: str) -> int:
    """First index of ``target`` at bracket depth 0; -1 if none."""
    depth = 0
    for i, ch in enumerate(s):
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(0, depth - 1)
        elif ch == target and depth == 0:
            return i
    return -1
