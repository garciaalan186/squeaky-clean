"""Tests for SiblingInterfaceFormatter."""

from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.sibling_interface_formatter import (
    SiblingInterfaceFormatter,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _module() -> ModuleSpec:
    title = ClassSpec(
        name="TodoTitle", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("value: str",),
        invariants=("title must be non-empty",),
    )
    todo = ClassSpec(
        name="Todo", pattern="Entity", implements=None,
        methods=("mark_complete(): None",),
        depends=("TodoTitle",), concretes=(),
        fields=("id: int", "title: TodoTitle"),
    )
    return ModuleSpec(
        name="Todo", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(title, todo), invariants=(),
    )


def test_formatter_includes_invariants_for_siblings() -> None:
    fmt = SiblingInterfaceFormatter(_TOOLKIT)
    out = fmt.format(_module(), focal_name="Todo")
    assert 'TodoTitle (ValueObject' in out
    assert 'invariants=["title must be non-empty"]' in out


def test_formatter_emits_empty_invariants_when_none() -> None:
    fmt = SiblingInterfaceFormatter(_TOOLKIT)
    out = fmt.format(_module(), focal_name="TodoTitle")
    assert "Todo (Entity" in out
    assert "invariants=[]" in out


def test_formatter_excludes_focal_class() -> None:
    fmt = SiblingInterfaceFormatter(_TOOLKIT)
    out = fmt.format(_module(), focal_name="Todo")
    assert "Todo (Entity" not in out


def test_formatter_includes_dotted_path_for_python() -> None:
    fmt = SiblingInterfaceFormatter(_TOOLKIT)
    out = fmt.format(_module(), focal_name="Todo")
    assert "file=src.domain.todo.todo_title" in out
