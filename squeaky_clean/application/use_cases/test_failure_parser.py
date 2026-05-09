"""TestFailureParser: extracts failing test file stems from raw runner output."""

import re
from pathlib import Path

from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PYTEST_FAILED: re.Pattern[str] = re.compile(r"FAILED\s+(\S+\.py)")
_PYTEST_ERROR: re.Pattern[str] = re.compile(r"ERROR\s+(\S+\.py)")
_NODE_PATH: re.Pattern[str] = re.compile(
    r"([^\s'\"()]+\.test\.(?:js|ts))"
)
_MAVEN_ERROR: re.Pattern[str] = re.compile(r"\[ERROR\]\s+(\w+Test)\.")
_MAVEN_ARROW: re.Pattern[str] = re.compile(r"<-\s+(\w+Test)\.")
_MAVEN_IN: re.Pattern[str] = re.compile(r"FAILURE!\s*--\s*in\s+\S*\.(\w+Test)\b")
_JAVA_COMPILE: re.Pattern[str] = re.compile(r"\[ERROR\]\s+(\S+\.java):\[\d+,\d+\]")
_TSC_ERROR: re.Pattern[str] = re.compile(
    r"(\S+\.ts)\(\d+,\d+\):\s*error\s+TS\d+"
)


class TestFailureParser:
    """Parses raw test-runner output into a tuple of failing test file stems.

    The returned stems are the source-file stems (e.g. ``operand`` for
    a failing ``tests/test_operand.py`` or ``tests/operand.test.js``,
    or ``OperandTest`` for a failing Java class). FixFailingClasses
    maps these stems back to the ImplementedClass instances whose
    source files should be repaired.
    """

    def parse(
        self, raw_output: str, language: TargetLanguage,
    ) -> tuple[str, ...]:
        """Return unique failing-test-file stems for ``language``."""
        if language is TargetLanguage.PYTHON:
            return self._pytest(raw_output)
        if language in (TargetLanguage.JAVASCRIPT, TargetLanguage.TYPESCRIPT):
            return self._node(raw_output)
        if language is TargetLanguage.JAVA:
            return self._maven(raw_output)
        return ()

    def _pytest(self, out: str) -> tuple[str, ...]:
        found: set[str] = set()
        for pattern in (_PYTEST_FAILED, _PYTEST_ERROR):
            for match in pattern.finditer(out):
                found.add(Path(match.group(1)).stem)
        return tuple(sorted(found))

    def _node(self, out: str) -> tuple[str, ...]:
        found: set[str] = set()
        for match in _NODE_PATH.finditer(out):
            stem = Path(match.group(1)).stem
            found.add(stem.removesuffix(".test"))
        for match in _TSC_ERROR.finditer(out):
            stem = Path(match.group(1)).stem
            found.add(stem.removesuffix(".test"))
        return tuple(sorted(found))

    def _maven(self, out: str) -> tuple[str, ...]:
        found: set[str] = set()
        for pattern in (_MAVEN_ERROR, _MAVEN_ARROW, _MAVEN_IN):
            for match in pattern.finditer(out):
                found.add(match.group(1))
        for match in _JAVA_COMPILE.finditer(out):
            found.add(Path(match.group(1)).stem)
        return tuple(sorted(found))
