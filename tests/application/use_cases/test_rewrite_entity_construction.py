"""Tests for RewriteEntityConstruction — object-literal -> constructor."""

from pathlib import Path

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.rewrite_entity_construction import (
    RewriteEntityConstruction,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _arch() -> ArchitectureSpec:
    cls = ClassSpec(
        name="ConsumedEvent", pattern="Entity", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("id: str", "received_at: str", "headers: dict", "payload: str"),
        invariants=())
    mod = ModuleSpec(name="Consumption", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(cls,), invariants=())
    return ArchitectureSpec.single(mod)


def _run(tmp_path: Path, src: str) -> str:
    (tmp_path / "src").mkdir()
    f = tmp_path / "src" / "adapter.ts"
    f.write_text(src)
    tk = LanguageToolkitFactory().for_language(TargetLanguage.TYPESCRIPT)
    RewriteEntityConstruction().rewrite(_arch(), tmp_path, tk)
    return f.read_text()


def test_rewrites_matching_object_literal(tmp_path: Path) -> None:
    src = ("function f(p: any): ConsumedEvent {\n"
           "  return {\n    id: p.id,\n    received_at: p.at,\n"
           "    headers: p.h as Record<string, string>,\n"
           "    payload: p.pl,\n  };\n}\n")
    out = _run(tmp_path, src)
    assert "new ConsumedEvent(p.id, p.at, p.h as Record<string, string>, p.pl)" in out
    assert "return {" not in out


def test_leaves_non_matching_literal_alone(tmp_path: Path) -> None:
    src = "function g(): any {\n  return { foo: 1, bar: 2 };\n}\n"
    out = _run(tmp_path, src)
    assert "return { foo: 1, bar: 2 }" in out  # keys don't match an entity


def test_python_is_untouched(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    f = tmp_path / "src" / "x.py"
    f.write_text("return {'id': 1}\n")
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    n = RewriteEntityConstruction().rewrite(_arch(), tmp_path, tk)
    assert n == 0
