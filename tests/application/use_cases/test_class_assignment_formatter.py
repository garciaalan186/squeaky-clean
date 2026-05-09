"""Tests for ClassAssignmentFormatter."""

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.use_cases.class_assignment_formatter import (
    ClassAssignmentFormatter,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _todo_module() -> ModuleSpec:
    todo = ClassSpec(
        name="Todo", pattern="Entity", implements=None,
        methods=("mark_complete(): None",),
        depends=("TodoTitle",), concretes=(),
        fields=("id: TodoId", "title: TodoTitle"),
    )
    title = ClassSpec(
        name="TodoTitle", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("value: str",),
    )
    return ModuleSpec(
        name="Todo", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(todo, title), invariants=(),
    )


def _assign(module: ModuleSpec, focal: str) -> ClassAssignment:
    spec = next(c for c in module.classes if c.name == focal)
    return ClassAssignment(
        class_spec=spec, module=module, toolkit=_TOOLKIT,
        icp_spec_name="EntityICP",
        file_path=f"/tmp/out/src/{focal.lower()}.py",
        test_file_path=f"/tmp/out/tests/test_{focal.lower()}.py",
    )


def test_formatter_emits_core_lines() -> None:
    out = ClassAssignmentFormatter(_TOOLKIT).format(
        _assign(_todo_module(), "Todo"),
    )
    assert "CLASS Todo" in out
    assert "PATTERN Entity" in out
    assert "FIELDS [id: TodoId, title: TodoTitle]" in out
    assert "METHODS [" in out
    assert "FILE_PATH /tmp/out/src/todo.py" in out


def test_formatter_emits_sibling_interfaces_block() -> None:
    out = ClassAssignmentFormatter(_TOOLKIT).format(
        _assign(_todo_module(), "Todo"),
    )
    assert "SIBLING_INTERFACES" in out
    assert "TodoTitle (ValueObject" in out
    assert "fields=[value: str]" in out
    assert "Todo (Entity" not in out


def test_formatter_lists_empty_fields_and_methods_for_sibling() -> None:
    a = ClassSpec(name="A", pattern="SimpleClass", implements=None,
                  methods=(), depends=(), concretes=())
    b = ClassSpec(name="B", pattern="SimpleClass", implements=None,
                  methods=(), depends=(), concretes=())
    module = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(a, b), invariants=())
    out = ClassAssignmentFormatter(_TOOLKIT).format(
        ClassAssignment(
            class_spec=a, module=module, toolkit=_TOOLKIT,
            icp_spec_name="SimpleClassICP",
            file_path="/tmp/a.py", test_file_path="/tmp/test_a.py",
        )
    )
    assert (
        "B (SimpleClass, file=src.domain.m.b): "
        "fields=[], methods=[], invariants=[]"
    ) in out


def _title_module() -> ModuleSpec:
    title = ClassSpec(
        name="TodoTitle", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("value: str",),
        invariants=("title must be non-empty",),
    )
    other = ClassSpec(
        name="Todo", pattern="Entity", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("id: int",),
    )
    return ModuleSpec(
        name="Todo", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(title, other), invariants=(),
    )


def test_formatter_emits_invariants_line_when_present() -> None:
    out = ClassAssignmentFormatter(_TOOLKIT).format(
        ClassAssignment(
            class_spec=_title_module().classes[0],
            module=_title_module(),
            toolkit=_TOOLKIT,
            icp_spec_name="ValueObjectICP",
            file_path="/tmp/todo_title.py",
            test_file_path="/tmp/test_todo_title.py",
        )
    )
    assert 'INVARIANTS ["title must be non-empty"]' in out


def test_formatter_omits_invariants_line_when_absent() -> None:
    out = ClassAssignmentFormatter(_TOOLKIT).format(
        _assign(_todo_module(), "TodoTitle"),
    )
    assert "INVARIANTS" not in out
