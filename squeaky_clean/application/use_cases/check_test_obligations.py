"""CheckTestObligations: verify generated tests discharge the spec contract.

Deterministic dual of ProjectTestObligations: reads the emitted test files
and confirms each obligation is discharged — the method is called AND an
assertion of the required kind is present in the same file. An obligation
with no such test is a gap (a missing or gamed/weakened test), independent
of whether the suite is green.
"""

from __future__ import annotations

import re
from pathlib import Path

from squeaky_clean.application.dtos.test_obligation import TestObligation
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind

_CTOR: str = "<init>"
_TEST_FILE = re.compile(r"(^test_.*\.py$|\.test\.(ts|js)$|Test\.java$)")
_RAISES: tuple[str, ...] = (
    "assertThrows", "assert.throws", "assert.rejects", ".rejects",
    "pytest.raises", "assertRaises", "toThrow", "fail(",
)
_EQUALS: tuple[str, ...] = (
    "assertEqual", "assertEquals", "assert.strictEqual", "assert.equal",
    "assert.deepStrictEqual", "assertSame", "toBe", "toEqual", "assert ",
)


class CheckTestObligations:
    """Reports obligations no generated test discharges."""

    def check(
        self, obligations: tuple[TestObligation, ...], output_dir: Path,
    ) -> tuple[TestObligation, ...]:
        """Return the subset of ``obligations`` not discharged by any test."""
        texts = self._test_texts(output_dir)
        return tuple(o for o in obligations if not self._discharged(o, texts))

    def _discharged(self, o: TestObligation, texts: list[str]) -> bool:
        return any(
            self._calls(o, t) and self._asserts(o.kind, t) for t in texts)

    def _calls(self, o: TestObligation, text: str) -> bool:
        forms = ({o.target_class} if o.method == _CTOR
                 else self._forms(o.method))
        return any(
            re.search(rf"\b{re.escape(f)}\s*\(", text) for f in forms)

    @staticmethod
    def _asserts(kind: AssertionKind, text: str) -> bool:
        if kind is AssertionKind.CALL_ONLY:
            return True
        if kind is AssertionKind.RAISES:
            return any(tok in text for tok in _RAISES)
        return any(tok in text for tok in _EQUALS)

    @staticmethod
    def _forms(name: str) -> set[str]:
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        parts = [p for p in snake.split("_") if p]
        camel = parts[0] + "".join(p.title() for p in parts[1:]) if parts else name
        return {name, snake, camel}

    @staticmethod
    def _test_texts(output_dir: Path) -> list[str]:
        out: list[str] = []
        for p in output_dir.rglob("*"):
            if not p.is_file() or not _TEST_FILE.search(p.name):
                continue
            if "node_modules" in p.parts or "target" in p.parts:
                continue
            try:
                out.append(p.read_text())
            except OSError:
                continue
        return out
