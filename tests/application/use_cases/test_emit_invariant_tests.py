"""Tests for the deterministic invariant-test emitter."""

from squeaky_clean.application.use_cases.emit_invariant_test_renderer import (
    InvariantTestRenderer,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _cls() -> ClassSpec:
    return ClassSpec(
        name="RawBody", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
        fields=("value: str", "sizeBytes: int"),
        invariants=("value must not be empty",
                    "sizeBytes must be <= 1048576"))


def _module(cls: ClassSpec) -> ModuleSpec:
    return ModuleSpec(name="Ingest", layer=LayerType.DOMAIN,
                      exports=(), depends=(), classes=(cls,), invariants=())


def _render(lang: TargetLanguage) -> tuple[str, str]:
    tk = LanguageToolkitFactory().for_language(lang)
    cls = _cls()
    return InvariantTestRenderer(tk).render(
        cls, _module(cls), cls.invariants)


def test_python_empty_and_numeric_bound() -> None:
    rel, body = _render(TargetLanguage.PYTHON)
    assert rel == "tests/test_raw_body_invariants.py"
    assert "pytest.raises(Exception)" in body
    assert 'RawBody("", 0)' in body           # empty violates "not empty"
    assert 'RawBody("x", 1048577)' in body    # 1048577 violates "<= 1048576"


def test_typescript_uses_node_test_and_throws() -> None:
    rel, body = _render(TargetLanguage.TYPESCRIPT)
    assert rel == "tests/rawBodyInvariants.test.ts"
    assert "node:test" in body and "assert.throws" in body
    assert "new RawBody('', 0)" in body
    assert "new RawBody('x', 1048577)" in body


def test_java_assert_throws() -> None:
    rel, body = _render(TargetLanguage.JAVA)
    assert rel.endswith("RawBodyInvariantsTest.java")
    assert "assertThrows(RuntimeException.class" in body
    assert 'new RawBody("", 0)' in body
    assert 'new RawBody("x", 1048577)' in body
