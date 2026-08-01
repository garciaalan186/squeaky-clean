"""Tests for the ``python -m squeaky_clean.interface.cli`` entrypoint."""

import inspect
import subprocess
import sys
from pathlib import Path

from squeaky_clean.interface.cli.__main__ import main

_APP_ROOT = Path(__file__).resolve().parents[3]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "squeaky_clean.interface.cli", *args],
        capture_output=True, text=True, cwd=_APP_ROOT, timeout=60, check=False,
    )


def test_main_is_importable_without_side_effects_and_takes_no_args() -> None:
    assert callable(main)
    assert list(inspect.signature(main).parameters) == []


def test_help_flag_exits_zero_with_usage() -> None:
    proc = _run_cli("--help")
    assert proc.returncode == 0
    assert "usage" in proc.stdout.lower()


def test_no_arguments_is_a_usage_error() -> None:
    proc = _run_cli()
    assert proc.returncode == 2
    assert "required" in proc.stderr
