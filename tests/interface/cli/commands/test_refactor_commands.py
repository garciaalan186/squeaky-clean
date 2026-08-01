"""Tests for RefactorCommands (triage + refactor-plan application)."""

from pathlib import Path

import pytest

from squeaky_clean.application.generation.recovery.squib.squib_emitter import SquibEmitter
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.interface.cli.commands.refactor_commands import RefactorCommands
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation

_SPEC = ArchitectureSpec(
    modules=(ModuleSpec(
        name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
        classes=(ClassSpec(
            name="Page", pattern="SimpleClass", implements=None,
            methods=("render(): str",), depends=(), concretes=(), fields=(),
            invariants=(),
        ),),
        invariants=(),
    ),),
    graph=ArchitectureGraph(edges={"Shop": ()}),
)


def test_refactor_emit_requires_a_plan(capsys: pytest.CaptureFixture[str]) -> None:
    rec = RecoveryInvocation(refactor="recovered.squib", plan=None)
    assert RefactorCommands().refactor_emit(rec) == 1
    assert "--refactor requires --plan" in capsys.readouterr().err


def test_refactor_emit_applies_plan_and_writes_output(tmp_path: Path) -> None:
    squib = tmp_path / "recovered.squib"
    squib.write_text(SquibEmitter().emit(_SPEC))
    plan = tmp_path / "refactor_plan.json"
    plan.write_text('{"fix": ["framework-coupling:app.page.Page"], "ignore": []}')
    out = tmp_path / "refactored.squib"
    rec = RecoveryInvocation(
        refactor=str(squib), plan=str(plan), refactor_out=str(out),
    )
    assert RefactorCommands().refactor_emit(rec) == 0
    assert out.is_file()
