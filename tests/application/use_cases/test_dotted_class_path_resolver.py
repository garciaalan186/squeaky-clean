"""Tests for DottedClassPathResolver — per-language dotted path mapping."""

from squeaky_clean.application.use_cases.dotted_class_path_resolver import (
    DottedClassPathResolver,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _module(name: str = "Archival", layer: LayerType = LayerType.DOMAIN) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=layer,
        exports=("ConsumedEvent",), depends=(),
        classes=(
            ClassSpec(
                name="ConsumedEvent", pattern="Entity", implements=None,
                methods=(), depends=(), concretes=(),
            ),
        ),
        invariants=(),
    )


def _resolve(lang: TargetLanguage) -> str:
    toolkit = LanguageToolkitFactory().for_language(lang)
    resolver = DottedClassPathResolver(toolkit)
    mod = _module()
    return resolver.resolve(mod.classes[0], mod)


def test_python_dotted_path_layered() -> None:
    assert _resolve(TargetLanguage.PYTHON) == "src.domain.archival.consumed_event"


def test_java_dotted_path_uses_com_example() -> None:
    assert _resolve(TargetLanguage.JAVA) == "com.example.ConsumedEvent"


def test_go_dotted_path_is_bare_class_name() -> None:
    assert _resolve(TargetLanguage.GO) == "ConsumedEvent"


def test_rust_dotted_path_uses_crate_prefix() -> None:
    assert _resolve(TargetLanguage.RUST) == "crate::consumed_event"


def test_javascript_dotted_path_uses_relative_src_path() -> None:
    assert _resolve(TargetLanguage.JAVASCRIPT) == "./src/consumedEvent"


def test_typescript_dotted_path_uses_relative_src_path() -> None:
    assert _resolve(TargetLanguage.TYPESCRIPT) == "./src/consumedEvent"
