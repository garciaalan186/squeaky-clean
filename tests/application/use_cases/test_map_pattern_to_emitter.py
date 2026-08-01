"""Tests for MapPatternToEmitter."""

from squeaky_clean.application.generation.emission.map_pattern_to_emitter import MapPatternToEmitter
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
_GO = LanguageToolkitFactory().for_language(TargetLanguage.GO)
_RUST = LanguageToolkitFactory().for_language(TargetLanguage.RUST)


def _map(pattern: str, toolkit: LanguageToolkit = _PY) -> str:
    return MapPatternToEmitter(toolkit).map(pattern)


def _map_for(
    pattern: PatternName, layer: LayerType, methods: tuple[str, ...], mode: str,
) -> str:
    cls = ClassSpec(
        name="Subject", pattern=pattern, implements=None,
        methods=methods, depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="M", layer=layer, exports=(), depends=(),
        classes=(cls,), invariants=(),
    )
    return MapPatternToEmitter(_PY, infrastructure_mode=mode).map_for(cls, module)


def test_strategy_maps_to_python_strategy_icp() -> None:
    assert _map("Strategy") == "python/behavioral/StrategyEmitter"


def test_entity_maps_to_python_entity_icp() -> None:
    assert _map("Entity") == "python/ddd_clean/EntityEmitter"


def test_value_object_maps_to_python_value_object_icp() -> None:
    assert _map("ValueObject") == "python/ddd_clean/ValueObjectEmitter"


def test_simple_class_maps_to_python_simple_class_icp() -> None:
    assert _map("SimpleClass") == "python/ddd_clean/SimpleClassEmitter"


def test_catalog_patterns_map_to_dedicated_icps() -> None:
    # Every GoF/DDD catalog pattern now resolves to its own ICP, never
    # silently degrading to SimpleClass.
    assert _map("Facade") == "python/structural/FacadeEmitter"
    assert _map("Observer") == "python/behavioral/ObserverEmitter"
    assert _map("AbstractFactory") == "python/creational/AbstractFactoryEmitter"


def test_unrecognized_pattern_falls_back_to_simple_class() -> None:
    # Only a genuinely unknown pattern name uses the escape hatch.
    assert _map("NotARealPattern") == "python/ddd_clean/SimpleClassEmitter"


def test_entity_maps_to_go_entity_icp() -> None:
    assert _map("Entity", _GO) == "go/ddd_clean/EntityEmitter"


def test_value_object_maps_to_go_value_object_icp() -> None:
    assert _map("ValueObject", _GO) == "go/ddd_clean/ValueObjectEmitter"


def test_strategy_maps_to_go_strategy_icp() -> None:
    assert _map("Strategy", _GO) == "go/behavioral/StrategyEmitter"


def test_simple_class_maps_to_go_simple_class_icp() -> None:
    assert _map("SimpleClass", _GO) == "go/ddd_clean/SimpleClassEmitter"


def test_entity_maps_to_rust_entity_icp() -> None:
    assert _map("Entity", _RUST) == "rust/ddd_clean/EntityEmitter"


def test_value_object_maps_to_rust_value_object_icp() -> None:
    assert _map("ValueObject", _RUST) == "rust/ddd_clean/ValueObjectEmitter"


def test_strategy_maps_to_rust_strategy_icp() -> None:
    assert _map("Strategy", _RUST) == "rust/behavioral/StrategyEmitter"


def test_simple_class_maps_to_rust_simple_class_icp() -> None:
    assert _map("SimpleClass", _RUST) == "rust/ddd_clean/SimpleClassEmitter"


def test_repository_in_infrastructure_with_blob_methods_routes_tier_c() -> None:
    """H1 — Repository on Infrastructure layer with put_blob/get_blob/delete_blob
    routes to BlobStorageAdapterEmitter when --infra=auto."""
    icp = _map_for(
        "Repository", LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"), "auto",
    )
    assert icp == "python/infrastructure/BlobStorageAdapterEmitter"


def test_repository_uses_catalog_icp_when_infra_mode_manual() -> None:
    """--infra=manual disables the Tier C path; Repository resolves to its
    dedicated catalog port ICP, not the SimpleClass escape hatch."""
    icp = _map_for(
        "Repository", LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"), "manual",
    )
    assert icp == "python/ddd_clean/RepositoryEmitter"


def test_repository_in_domain_layer_never_routes_tier_c() -> None:
    icp = _map_for(
        "Repository", LayerType.DOMAIN, ("put_blob", "get_blob"), "auto",
    )
    assert icp == "python/ddd_clean/RepositoryEmitter"


def test_application_gateway_maps_to_gateway_icp() -> None:
    ts = LanguageToolkitFactory().for_language(TargetLanguage.TYPESCRIPT)
    java = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    assert _map("Gateway") == "python/ddd_clean/GatewayEmitter"
    assert _map("Gateway", ts) == "typescript/ddd_clean/GatewayEmitter"
    assert _map("Gateway", java) == "java/ddd_clean/GatewayEmitter"


def test_gateway_resolves_for_all_languages() -> None:
    # GatewayEmitter now exists for every supported language.
    assert _map("Gateway", _GO) == "go/ddd_clean/GatewayEmitter"
    assert _map("Gateway", _RUST) == "rust/ddd_clean/GatewayEmitter"


def test_declared_categories_break_ties_when_verbs_are_ambiguous() -> None:
    """register_category supplies the ProblemSpec's explicit choice when the
    verb heuristic cannot infer a category."""
    cls = ClassSpec(
        name="Store", pattern="Repository", implements=None,
        methods=("frobnicate",), depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="M", layer=LayerType.INFRASTRUCTURE, exports=(), depends=(),
        classes=(cls,), invariants=(),
    )
    mapper = MapPatternToEmitter(_PY, infrastructure_mode="auto")
    mapper.register_category("kv_cache")
    assert mapper.map_for(cls, module) == "python/infrastructure/KvCacheEmitter"
