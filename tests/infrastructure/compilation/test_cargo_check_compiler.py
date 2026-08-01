"""Tests for CargoCheckCompiler (R6.1d rust micro-eval column)."""

import shutil
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.compilation.cargo_check_compiler import (
    CargoCheckCompiler,
)

pytestmark = pytest.mark.skipif(
    shutil.which("cargo") is None, reason="cargo toolchain not installed",
)

_MANIFEST = '[package]\nname = "microeval"\nversion = "0.1.0"\nedition = "2021"\n'


def _cell(tmp_path: Path, files: dict[str, str]) -> Path:
    (tmp_path / "Cargo.toml").write_text(_MANIFEST)
    (tmp_path / "src").mkdir()
    for name, body in files.items():
        (tmp_path / "src" / name).write_text(body)
    return tmp_path


def test_valid_modules_check_clean(tmp_path: Path) -> None:
    result = CargoCheckCompiler().compile(_cell(tmp_path, {
        "point.rs": "pub struct Point { pub x: i64 }\n",
    }))
    assert result.ok
    assert (tmp_path / "src" / "lib.rs").read_text() == "pub mod point;\n"


def test_compile_error_reports_offending_stem(tmp_path: Path) -> None:
    result = CargoCheckCompiler().compile(_cell(tmp_path, {
        "broken.rs": "pub struct Broken { pub x: NoSuchType }\n",
        "fine.rs": "pub struct Fine { pub y: i64 }\n",
    }))
    assert not result.ok
    assert result.error_count >= 1
    assert "broken" in result.offending_stems


def test_missing_toolchain_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    with pytest.raises(RuntimeError, match="cargo toolchain"):
        CargoCheckCompiler().compile(tmp_path)
