"""Tests for EmitJavaEntitySerialization — deterministic Java toJson()."""

from pathlib import Path

from squeaky_clean.application.use_cases.emit_java_entity_serialization import (
    EmitJavaEntitySerialization,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
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
        fields=("id: str", "received_at: str", "headers: dict[str, str]"),
        invariants=())
    mod = ModuleSpec(name="Consumption", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(cls,), invariants=())
    return ArchitectureSpec.single(mod)


def _entity_file(tmp_path: Path) -> Path:
    d = tmp_path / "src" / "main" / "java" / "com" / "example"
    d.mkdir(parents=True)
    f = d / "ConsumedEvent.java"
    f.write_text("package com.example;\nclass ConsumedEvent {\n}\n")
    return f


def test_injects_tojson_when_called(tmp_path: Path) -> None:
    entity = _entity_file(tmp_path)
    (tmp_path / "src" / "uc.java").write_text(
        "class Uc { void f(ConsumedEvent event) { event.toJson(); } }")
    tk = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    n = EmitJavaEntitySerialization().emit(_arch(), tmp_path, tk)
    body = entity.read_text()
    assert n == 1
    assert "public String toJson()" in body
    assert '\\"received_at\\":' in body      # exact snake_case key
    assert "toJsonMap(this.headers)" in body  # Map handled


def test_skipped_when_never_called(tmp_path: Path) -> None:
    _entity_file(tmp_path)
    tk = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    assert EmitJavaEntitySerialization().emit(_arch(), tmp_path, tk) == 0
