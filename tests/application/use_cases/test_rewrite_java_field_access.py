"""Tests for RewriteJavaFieldAccess — VO field read -> getter call."""

from pathlib import Path

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.rewrite_java_field_access import (
    RewriteJavaFieldAccess,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _arch() -> ArchitectureSpec:
    cls = ClassSpec(
        name="BlobKey", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("value: str",), invariants=())
    mod = ModuleSpec(name="Archival", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(cls,), invariants=())
    return ArchitectureSpec.single(mod)


def _run(tmp_path: Path, src: str) -> str:
    (tmp_path / "src").mkdir()
    f = tmp_path / "src" / "Adapter.java"
    f.write_text(src)
    tk = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    RewriteJavaFieldAccess().rewrite(_arch(), tmp_path, tk)
    return f.read_text()


def test_rewrites_field_read_to_getter(tmp_path: Path) -> None:
    out = _run(tmp_path, "void write(BlobKey key) { String k = key.value; }")
    assert "key.getValue()" in out and "key.value;" not in out


def test_leaves_method_calls_and_unknown_vars(tmp_path: Path) -> None:
    out = _run(tmp_path, "void f(BlobKey key) { key.getValue(); other.value; }")
    assert "key.getValue();" in out
    assert "other.value;" in out  # 'other' is not a VO-typed variable
