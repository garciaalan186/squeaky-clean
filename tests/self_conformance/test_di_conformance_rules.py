"""Unit tests for the R6.4 DI-regime conformance rules."""

from pathlib import Path

from tests.self_conformance.di_conformance_rules import (
    fs_port_bypass_keys,
    impure_construction_keys,
)

_GEN = "squeaky_clean/application/generation/x/mod.py"
_EVAL = "squeaky_clean/application/evaluation/x/mod.py"
_APP = "squeaky_clean/application/shared/x/mod.py"


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "mod.py"
    p.write_text(body)
    return p


def test_raw_write_flagged_in_generation(tmp_path: Path) -> None:
    p = _write(tmp_path, "def f(path):\n    path.write_text('x')\n")
    assert fs_port_bypass_keys(p, _GEN) == {
        f"FsPortBypass|{_GEN}|raw Path write in generation/"
    }


def test_raw_write_flagged_in_evaluation(tmp_path: Path) -> None:
    p = _write(tmp_path, "def f(path):\n    path.write_bytes(b'x')\n")
    assert fs_port_bypass_keys(p, _EVAL) == {
        f"FsPortBypass|{_EVAL}|non-atomic write in evaluation/"
    }


def test_atomic_helper_and_port_calls_pass(tmp_path: Path) -> None:
    body = (
        "def f(fs, path):\n"
        "    atomic_write_text(path, 'x')\n"
        "    fs.write(path, 'x')\n"
        "    path.mkdir(parents=True, exist_ok=True)\n"
    )
    p = _write(tmp_path, body)
    assert fs_port_bypass_keys(p, _GEN) == set()
    assert fs_port_bypass_keys(p, _EVAL) == set()


def test_scope_excludes_other_layers(tmp_path: Path) -> None:
    p = _write(tmp_path, "def f(path):\n    path.write_text('x')\n")
    assert fs_port_bypass_keys(p, _APP) == set()


def test_denylisted_construction_flagged(tmp_path: Path) -> None:
    p = _write(tmp_path, "def f(x):\n    return x or LoadAgentSpec()\n")
    assert impure_construction_keys(p, _APP) == {
        f"ImpureConstruction|{_APP}|LoadAgentSpec constructed in application"
    }


def test_type_reference_is_not_construction(tmp_path: Path) -> None:
    body = (
        "def f(loader: LoadAgentSpec) -> LoadAgentSpec:\n"
        "    return loader\n"
    )
    p = _write(tmp_path, body)
    assert impure_construction_keys(p, _APP) == set()
