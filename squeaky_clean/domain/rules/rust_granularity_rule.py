"""RustGranularityRule: size/method/arg limits for .rs source files."""

import re
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule

_PUB_FN: re.Pattern[str] = re.compile(
    r"^\s*pub\s+fn\s+([a-z_]\w*)\s*\(([^)]*)\)", re.MULTILINE,
)
_IMPL_HEAD: re.Pattern[str] = re.compile(
    r"^\s*impl(?:\s*<[^>]+>)?\s+(?:[\w:]+\s+for\s+)?([\w:]+)", re.MULTILINE,
)


class RustGranularityRule(Rule):
    """Parses one Rust file and flags granularity violations.

    Detects ``pub fn`` declarations both as free functions and inside
    ``impl`` blocks. Enforces <=80 lines/file, <=5 pub fns per impl
    block, and <=2 args per method (excluding ``self`` receivers).
    Skips ``target/`` and ``tests/`` directories.
    """

    _NAME = "RustGranularityRule"
    _MAX_LINES = 80
    _MAX_METHODS = 5
    _MAX_ARGS = 2
    _SELF_TOKENS: tuple[str, ...] = ("&self", "&mut self", "self")

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .rs file and return any granularity violations."""
        if path.suffix != ".rs":
            return []
        if "target" in path.parts or "tests" in path.parts:
            return []
        source = path.read_text()
        out: list[Violation] = []
        line_count = len(source.splitlines())
        if line_count > self._MAX_LINES:
            out.append(self._v(path, f"file has {line_count} lines (>80)"))
        out.extend(self._check_fns(source, path))
        return out

    def _check_fns(self, source: str, path: Path) -> list[Violation]:
        out: list[Violation] = []
        impls = list(_IMPL_HEAD.finditer(source))
        if len(impls) > 1:
            out.append(self._v(path, f"file declares {len(impls)} impl blocks (>1)"))
        fn_count = 0
        for name, params in _PUB_FN.findall(source):
            fn_count += 1
            count = self._count_args(params)
            if count > self._MAX_ARGS:
                out.append(self._v(path, f"{name} has {count} args (>2)"))
        if fn_count > self._MAX_METHODS:
            out.append(self._v(path, f"file has {fn_count} pub fns (>5)"))
        return out

    def _count_args(self, params: str) -> int:
        stripped = params.strip()
        if not stripped:
            return 0
        parts = [p.strip() for p in stripped.split(",") if p.strip()]
        non_self = [p for p in parts if p not in self._SELF_TOKENS]
        return len(non_self)

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(rule_name=self._NAME, file_path=str(path), message=message)
