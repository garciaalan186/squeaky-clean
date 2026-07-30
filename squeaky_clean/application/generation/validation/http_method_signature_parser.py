"""http_method_signature_parser: split a §Notation method declaration into parts."""

from __future__ import annotations


def parse_method(method: str) -> tuple[str, list[tuple[str, str]], str]:
    """Parse 'name(arg: Type, arg2: Type2): ReturnType' into name/args/return.

    Returns ``(name, [(arg_name, arg_type), ...], return_type)``. Splits
    on top-level commas only — commas inside ``[]``, ``()``, ``<>``,
    ``{}`` are part of the type (e.g. ``dict[str, str]`` and
    ``Map<String, String>`` stay intact).
    """
    if "(" not in method or ")" not in method:
        return (method.strip(), [], "")
    name, _, rest = method.partition("(")
    inner, _, after = _split_balanced_parens(rest)
    ret = after.lstrip(": ").strip()
    args: list[tuple[str, str]] = []
    for part in _split_top_level(inner):
        if ":" in part:
            an, _, at = part.partition(":")
            args.append((an.strip(), at.strip()))
    return (name.strip(), args, ret)


def _split_balanced_parens(rest: str) -> tuple[str, str, str]:
    """Find matching ')' for the implicit opening paren consumed by caller."""
    depth = 1
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return rest[:i], ")", rest[i + 1:]
    return rest, "", ""


def _split_top_level(s: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in s:
        if ch in "[(<{":
            depth += 1
        elif ch in "])>}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts
