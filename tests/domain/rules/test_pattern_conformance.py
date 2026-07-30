"""Tests for PatternConformanceRule (R2.5)."""

from pathlib import Path

from squeaky_clean.domain.rules.pattern_conformance import PatternConformanceRule


def _check(tmp_path: Path, code: str) -> list[str]:
    f = tmp_path / "node.py"
    f.write_text(code)
    return [v.message for v in PatternConformanceRule().check(f)]


def test_valid_visitor_accept_passes(tmp_path: Path) -> None:
    code = (
        "class Circle:\n"
        "    def accept(self, visitor):\n"
        "        return visitor.visit_circle(self)\n"
    )
    assert _check(tmp_path, code) == []


def test_stubbed_accept_is_flagged(tmp_path: Path) -> None:
    code = (
        "class Circle:\n"
        "    def accept(self, visitor):\n"
        "        pass\n"
    )
    msgs = _check(tmp_path, code)
    assert len(msgs) == 1
    assert "double dispatch" in msgs[0]


def test_accept_without_visit_call_is_flagged(tmp_path: Path) -> None:
    code = (
        "class Circle:\n"
        "    def accept(self, visitor):\n"
        "        return self.area()\n"
    )
    assert len(_check(tmp_path, code)) == 1


def test_class_without_accept_is_ignored(tmp_path: Path) -> None:
    code = "class Money:\n    def add(self, other):\n        return self\n"
    assert _check(tmp_path, code) == []


def test_non_python_file_ignored(tmp_path: Path) -> None:
    f = tmp_path / "Node.java"
    f.write_text("class Node { void accept(Visitor v) {} }")
    assert PatternConformanceRule().check(f) == []
