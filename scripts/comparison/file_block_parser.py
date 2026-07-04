"""Parse `### File: path/to/file.ext` markers + fenced code blocks.

The OUTPUT FORMAT both Squeaky's prose translator and the framing #1 brief
specify: each emitted source file is preceded by a header line of the form
`### File: path/to/file.py` and is wrapped in a fenced code block. This
parser is regex-based and deterministic; if the LLM violates the format,
the run is marked parse_failure rather than silently coerced.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FILE_HEADER = re.compile(
    r"^###\s+File:\s+(?P<path>[A-Za-z0-9_./-]+)\s*$",
    re.MULTILINE,
)
_FENCE = re.compile(r"^```[A-Za-z0-9_+-]*\s*\n(?P<body>.*?)^```\s*$", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class ParsedFile:
    """One file-block extracted from a baseline LLM completion."""

    path: str
    content: str


@dataclass(frozen=True)
class ParseResult:
    """Outcome of parsing a baseline output."""

    files: tuple[ParsedFile, ...]
    parse_failure: bool
    failure_reason: str = ""


def parse_baseline_output(text: str) -> ParseResult:
    """Extract file-blocks from `### File: ...` + fenced-code outputs.

    A successful parse: every header has a fenced block immediately after,
    and there is at least one (header, block) pair. A parse failure is
    returned with a reason string; callers should record the failure on
    BaselineComparisonMetrics rather than guess what the LLM meant.
    """
    headers = list(_FILE_HEADER.finditer(text))
    if not headers:
        return ParseResult(
            files=(),
            parse_failure=True,
            failure_reason="no `### File:` headers found",
        )
    fences = list(_FENCE.finditer(text))
    files: list[ParsedFile] = []
    for header in headers:
        path = header.group("path")
        next_fence = _next_fence_after(fences, header.start())
        if next_fence is None:
            return ParseResult(
                files=tuple(files),
                parse_failure=True,
                failure_reason=f"header `### File: {path}` has no fenced block after it",
            )
        files.append(ParsedFile(path=path, content=next_fence.group("body").rstrip("\n") + "\n"))
    return ParseResult(files=tuple(files), parse_failure=False)


def _next_fence_after(fences: list[re.Match[str]], offset: int) -> re.Match[str] | None:
    for fence in fences:
        if fence.start() > offset:
            return fence
    return None
