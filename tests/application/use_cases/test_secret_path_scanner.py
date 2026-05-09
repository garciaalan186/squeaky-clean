"""Unit tests for SecretPathScanner (recursive directory secret scanning)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.secret_path_scanner import SecretPathScanner
from squeaky_clean.application.use_cases.secret_scanner import SecretScanner

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "scan_for_secrets.py"
_FAKE_KEY = "sk-ant" + "-abc123ABCDEF0123456789"
_FAKE_KEY_LONG = "sk-ant" + "-abcdefghij0123456789ABC"


def test_anthropic_key_in_file_triggers_hit(tmp_path: Path) -> None:
    f = tmp_path / "leak.py"
    f.write_text(f"API = '{_FAKE_KEY}'\n")
    hits = SecretPathScanner().scan(tmp_path)
    assert any("anthropic_api_key" in h.label for h in hits)
    assert hits[0].line == 1


def test_low_entropy_random_words_do_not_trigger(tmp_path: Path) -> None:
    f = tmp_path / "ok.py"
    f.write_text("not-a-key-just-random-words-1234\n")
    assert SecretPathScanner().scan(tmp_path) == ()


def test_dotenv_filename_blocked_without_reading_contents(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("")  # empty contents
    hits = SecretPathScanner().scan(tmp_path)
    assert any("blocked_filename:.env" in h.label for h in hits)


def test_pem_suffix_blocked(tmp_path: Path) -> None:
    (tmp_path / "key.pem").write_text("benign content")
    hits = SecretPathScanner().scan(tmp_path)
    assert any("blocked_suffix:.pem" in h.label for h in hits)


def test_oversized_file_skipped(tmp_path: Path) -> None:
    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * (101 * 1024))
    assert SecretPathScanner().scan(tmp_path) == ()


def test_binary_suffix_skipped(tmp_path: Path) -> None:
    f = tmp_path / "image.png"
    f.write_bytes(_FAKE_KEY.encode())
    assert SecretPathScanner().scan(tmp_path) == ()


def test_filename_blocked_helper() -> None:
    s = SecretScanner()
    assert s.filename_blocked(".env") == "blocked_filename:.env"
    assert s.filename_blocked("foo.pem") == "blocked_suffix:.pem"
    assert s.filename_blocked("ok.py") is None


def _run(target: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    if env is not None:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(target)],
        capture_output=True, text=True, check=False, env=full_env,
    )


def test_scan_script_clean_returns_zero(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("hello world\n")
    proc = _run(tmp_path)
    assert proc.returncode == 0


def test_scan_script_finds_secret_returns_one(tmp_path: Path) -> None:
    (tmp_path / "leak.py").write_text(f"k = '{_FAKE_KEY_LONG}'\n")
    proc = _run(tmp_path)
    assert proc.returncode == 1
    assert "anthropic_api_key" in proc.stderr


def test_scan_script_bypass_env_var_overrides(tmp_path: Path) -> None:
    (tmp_path / "leak.py").write_text(f"k = '{_FAKE_KEY_LONG}'\n")
    proc = _run(tmp_path, env={"SECRET_SCAN_BYPASS": "1"})
    assert proc.returncode == 0
    assert "BYPASSED" in proc.stderr


@pytest.mark.parametrize("missing", ["does_not_exist_xyz"])
def test_scan_script_missing_path_returns_two(tmp_path: Path, missing: str) -> None:
    proc = _run(tmp_path / missing)
    assert proc.returncode == 2
