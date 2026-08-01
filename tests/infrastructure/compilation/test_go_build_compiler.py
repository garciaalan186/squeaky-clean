"""Tests for GoBuildCompiler (R6.1d go micro-eval column)."""

import shutil
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.compilation.go_build_compiler import GoBuildCompiler

pytestmark = pytest.mark.skipif(
    shutil.which("go") is None, reason="go toolchain not installed",
)


def _cell(tmp_path: Path, files: dict[str, str]) -> Path:
    (tmp_path / "go.mod").write_text("module microeval\n\ngo 1.18\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "zz_main.go").write_text(
        "package main\n\nfunc main() {}\n",
    )
    for name, body in files.items():
        (tmp_path / "src" / name).write_text(body)
    return tmp_path


def test_valid_package_builds(tmp_path: Path) -> None:
    result = GoBuildCompiler().compile(_cell(tmp_path, {
        "point.go": "package main\n\ntype Point struct{ X int }\n",
    }))
    assert result.ok
    assert result.error_count == 0


def test_compile_error_reports_offending_stem(tmp_path: Path) -> None:
    result = GoBuildCompiler().compile(_cell(tmp_path, {
        "broken.go": "package main\n\ntype Broken struct{ X undefinedType }\n",
        "fine.go": "package main\n\ntype Fine struct{ Y int }\n",
    }))
    assert not result.ok
    assert result.error_count >= 1
    assert "broken" in result.offending_stems


def test_missing_toolchain_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    with pytest.raises(RuntimeError, match="go toolchain"):
        GoBuildCompiler().compile(tmp_path)
