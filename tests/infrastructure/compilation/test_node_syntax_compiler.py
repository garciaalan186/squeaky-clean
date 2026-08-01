"""Tests for NodeSyntaxCompiler (R6.1d js micro-eval column)."""

import shutil
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.compilation.node_syntax_compiler import (
    NodeSyntaxCompiler,
)

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="node toolchain not installed",
)


def _project(tmp_path: Path, files: dict[str, str]) -> Path:
    (tmp_path / "package.json").write_text('{"type": "module"}')
    for name, body in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    return tmp_path


def test_valid_esm_passes(tmp_path: Path) -> None:
    result = NodeSyntaxCompiler().compile(_project(tmp_path, {
        "src/payment.js": "export class Payment { pay() { return 1; } }\n",
    }))
    assert result.ok
    assert result.error_count == 0


def test_syntax_error_is_reported_with_stem(tmp_path: Path) -> None:
    result = NodeSyntaxCompiler().compile(_project(tmp_path, {
        "src/broken.js": "export class { nope(\n",
        "src/fine.js": "export class Fine {}\n",
    }))
    assert not result.ok
    assert result.error_count == 1
    assert result.offending_stems == ("broken",)


def test_node_modules_are_ignored(tmp_path: Path) -> None:
    result = NodeSyntaxCompiler().compile(_project(tmp_path, {
        "node_modules/dep/bad.js": "not javascript at all (",
        "src/ok.js": "export class Ok {}\n",
    }))
    assert result.ok
