"""Tests for SquibReviewGate: emit, reload, and line-context errors."""

from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.recovery.squib_review_error import (
    SquibReviewError,
)
from squeaky_clean.application.use_cases.recovery.squib_review_gate import (
    SquibReviewGate,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_ORDER = ClassSpec(
    name="Order", pattern="Entity", implements=None,
    methods=("total(): int",), depends=(), concretes=(), fields=("id: str",),
)
_MODULE = ModuleSpec(
    name="Shop", layer=LayerType.DOMAIN, exports=(),
    depends=(), classes=(_ORDER,), invariants=(),
)
_SPEC = ArchitectureSpec.single(_MODULE)

_BAD_PATTERN = (
    "MODULE Shop\nLAYER Domain\nEXPORTS []\nDEPENDS []\nCLASSES {\n"
    "  Order -> Xyz {\n    fields: [id: str]\n    methods: [total(): int]\n"
    "  }\n}\nINVARIANTS []\n"
)


def test_emit_then_load_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "review" / "recovered.squib"
    gate = SquibReviewGate()
    gate.emit(_SPEC, path)
    assert path.exists()
    assert gate.load(path).modules == _SPEC.modules


def test_load_reports_unknown_pattern_with_line_context(tmp_path: Path) -> None:
    path = tmp_path / "recovered.squib"
    path.write_text(_BAD_PATTERN)
    with pytest.raises(SquibReviewError) as info:
        SquibReviewGate().load(path)
    assert info.value.line == 6
    assert "Xyz" in info.value.snippet


def test_load_reports_missing_module_without_a_line(tmp_path: Path) -> None:
    path = tmp_path / "empty.squib"
    path.write_text("LAYER Domain\nCLASSES {\n}\n")
    with pytest.raises(SquibReviewError) as info:
        SquibReviewGate().load(path)
    assert info.value.line is None
