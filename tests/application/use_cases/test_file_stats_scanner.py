"""Tests for FileStatsScanner."""

from pathlib import Path

from squeaky_clean.application.use_cases.file_stats_scanner import FileStatsScanner


def _write(root: Path, rel: str, content: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_missing_dir_returns_zero_stats(tmp_path: Path) -> None:
    fs = FileStatsScanner().scan(tmp_path / "nope")
    assert fs.avg_line_count == 0.0
    assert fs.max_line_count == 0
    assert fs.orphan_count == 0


def test_scan_python_project(tmp_path: Path) -> None:
    _write(tmp_path, "src/foo.py", "class Foo:\n    pass\n")
    _write(tmp_path, "src/bar.py", "from foo import Foo\n\nclass Bar:\n    pass\n")
    _write(tmp_path, "src/__init__.py", "")
    stats = FileStatsScanner().scan(tmp_path)
    assert stats.max_line_count == 4
    assert stats.avg_line_count == 3.0
    # foo is imported, bar is orphan
    assert stats.orphan_count == 1


def test_scan_javascript_project(tmp_path: Path) -> None:
    _write(tmp_path, "src/calc.js", "export class Calc {}\n")
    _write(
        tmp_path,
        "src/main.js",
        "import { Calc } from './calc.js';\nconst c = new Calc();\n",
    )
    stats = FileStatsScanner().scan(tmp_path)
    assert stats.max_line_count >= 1
    assert stats.orphan_count == 1  # only main is orphan (calc is imported)


def test_skips_harness_files(tmp_path: Path) -> None:
    _write(tmp_path, "src/foo.py", "class Foo: pass\n")
    _write(tmp_path, "tests/conftest.py", "# conftest\n")
    _write(tmp_path, "package.json", "{}\n")
    stats = FileStatsScanner().scan(tmp_path)
    # Only foo.py counted (both filtered out)
    assert stats.max_line_count == 1
    assert stats.avg_line_count == 1.0
