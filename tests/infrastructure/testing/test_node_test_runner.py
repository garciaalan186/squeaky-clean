"""Tests for NodeTestRunner."""

import shutil
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner

# R5.9: these tests invoke the real `node` binary; skip (don't fail) on
# machines without it so the suite is honest about what it measured.
pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="node not on PATH",
)


def _bootstrap(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"type": "module"}\n')
    (tmp_path / "tests").mkdir()


def test_node_test_runner_runs_passing_test(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    (tmp_path / "tests" / "ok.test.js").write_text(
        "import { test } from 'node:test';\n"
        "import assert from 'node:assert/strict';\n"
        "test('ok', () => { assert.strictEqual(1, 1); });\n"
    )
    result = NodeTestRunner().run(tmp_path)
    assert result.passed == 1
    assert result.failed == 0


def test_node_test_runner_reports_failures(tmp_path: Path) -> None:
    _bootstrap(tmp_path)
    (tmp_path / "tests" / "bad.test.js").write_text(
        "import { test } from 'node:test';\n"
        "import assert from 'node:assert/strict';\n"
        "test('bad', () => { assert.strictEqual(1, 2); });\n"
    )
    result = NodeTestRunner().run(tmp_path)
    assert result.passed == 0
    assert result.failed == 1
