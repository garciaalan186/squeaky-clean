"""Tests for RecoverCommands.emit (ingest -> Squib + violations sidecars)."""

from pathlib import Path

import pytest

from squeaky_clean.interface.cli.commands.recover_commands import RecoverCommands
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation

_ORDER = (
    "from dataclasses import dataclass\n\n\n"
    "@dataclass\nclass Order:\n    id: str\n\n"
    "    def total(self) -> int:\n        return 0\n"
)


def test_emit_writes_squib_and_violation_sidecars(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    (project / "shop").mkdir(parents=True)
    (project / "shop" / "__init__.py").write_text("")
    (project / "shop" / "order.py").write_text(_ORDER)
    out = tmp_path / "out" / "recovered.squib"
    rec = RecoveryInvocation(
        recover_from=str(project), recover_out=str(out),
        recover_language="python",
    )
    assert RecoverCommands().emit(rec) == 0
    assert out.is_file()
    assert out.with_name(out.name + ".violations.json").is_file()
    assert out.with_name(out.name + ".violations.md").is_file()


def test_emit_defaults_output_to_cwd_recovered_squib(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "proj"
    (project / "shop").mkdir(parents=True)
    (project / "shop" / "__init__.py").write_text("")
    (project / "shop" / "order.py").write_text(_ORDER)
    rec = RecoveryInvocation(recover_from=str(project), recover_language="python")
    assert RecoverCommands().emit(rec) == 0
    assert (tmp_path / "recovered.squib").is_file()
