"""Tests for MapPatternToEmitter."""

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.map_pattern_to_emitter import MapPatternToEmitter
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
_GO = LanguageToolkitFactory().for_language(TargetLanguage.GO)
_RUST = LanguageToolkitFactory().for_language(TargetLanguage.RUST)


def test_strategy_maps_to_python_strategy_icp() -> None:
    assert MapPatternToEmitter().map("Strategy", _PY) == "python/behavioral/StrategyEmitter"


def test_entity_maps_to_python_entity_icp() -> None:
    assert MapPatternToEmitter().map("Entity", _PY) == "python/ddd_clean/EntityEmitter"


def test_value_object_maps_to_python_value_object_icp() -> None:
    assert (
        MapPatternToEmitter().map("ValueObject", _PY)
        == "python/ddd_clean/ValueObjectEmitter"
    )


def test_simple_class_maps_to_python_simple_class_icp() -> None:
    assert (
        MapPatternToEmitter().map("SimpleClass", _PY)
        == "python/ddd_clean/SimpleClassEmitter"
    )


def test_catalog_patterns_map_to_dedicated_icps() -> None:
    # Every GoF/DDD catalog pattern now resolves to its own ICP, never
    # silently degrading to SimpleClass.
    assert MapPatternToEmitter().map("Facade", _PY) == "python/structural/FacadeEmitter"
    assert MapPatternToEmitter().map("Observer", _PY) == "python/behavioral/ObserverEmitter"
    assert (
        MapPatternToEmitter().map("AbstractFactory", _PY)
        == "python/creational/AbstractFactoryEmitter"
    )


def test_unrecognized_pattern_falls_back_to_simple_class() -> None:
    # Only a genuinely unknown pattern name uses the escape hatch.
    assert (
        MapPatternToEmitter().map("NotARealPattern", _PY)
        == "python/ddd_clean/SimpleClassEmitter"
    )


def test_entity_maps_to_go_entity_icp() -> None:
    assert MapPatternToEmitter().map("Entity", _GO) == "go/ddd_clean/EntityEmitter"


def test_value_object_maps_to_go_value_object_icp() -> None:
    assert (
        MapPatternToEmitter().map("ValueObject", _GO)
        == "go/ddd_clean/ValueObjectEmitter"
    )


def test_strategy_maps_to_go_strategy_icp() -> None:
    assert MapPatternToEmitter().map("Strategy", _GO) == "go/behavioral/StrategyEmitter"


def test_simple_class_maps_to_go_simple_class_icp() -> None:
    assert (
        MapPatternToEmitter().map("SimpleClass", _GO)
        == "go/ddd_clean/SimpleClassEmitter"
    )


def test_entity_maps_to_rust_entity_icp() -> None:
    assert MapPatternToEmitter().map("Entity", _RUST) == "rust/ddd_clean/EntityEmitter"


def test_value_object_maps_to_rust_value_object_icp() -> None:
    assert (
        MapPatternToEmitter().map("ValueObject", _RUST)
        == "rust/ddd_clean/ValueObjectEmitter"
    )


def test_strategy_maps_to_rust_strategy_icp() -> None:
    assert (
        MapPatternToEmitter().map("Strategy", _RUST)
        == "rust/behavioral/StrategyEmitter"
    )


def test_simple_class_maps_to_rust_simple_class_icp() -> None:
    assert (
        MapPatternToEmitter().map("SimpleClass", _RUST)
        == "rust/ddd_clean/SimpleClassEmitter"
    )


def test_repository_in_infrastructure_with_blob_methods_routes_tier_c() -> None:
    """H1 — Repository on Infrastructure layer with put_blob/get_blob/delete_blob
    routes to BlobStorageAdapterEmitter when --infra=auto."""
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/BlobStorageAdapterEmitter"


def test_repository_uses_catalog_icp_when_infra_mode_manual() -> None:
    """--infra=manual disables the Tier C path; Repository resolves to its
    dedicated catalog port ICP, not the SimpleClass escape hatch."""
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"),
        infrastructure_mode="manual",
    )
    assert icp == "python/ddd_clean/RepositoryEmitter"


def test_repository_in_domain_layer_never_routes_tier_c() -> None:
    icp = MapPatternToEmitter().map_with_layer(
        "Repository", _PY, LayerType.DOMAIN,
        ("put_blob", "get_blob"),
        infrastructure_mode="auto",
    )
    assert icp == "python/ddd_clean/RepositoryEmitter"


def test_application_gateway_maps_to_gateway_icp() -> None:
    _TS = LanguageToolkitFactory().for_language(TargetLanguage.TYPESCRIPT)
    _JAVA = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    assert MapPatternToEmitter().map("Gateway", _PY) == "python/ddd_clean/GatewayEmitter"
    assert MapPatternToEmitter().map("Gateway", _TS) == "typescript/ddd_clean/GatewayEmitter"
    assert MapPatternToEmitter().map("Gateway", _JAVA) == "java/ddd_clean/GatewayEmitter"


def test_gateway_resolves_for_all_languages() -> None:
    # GatewayEmitter now exists for every supported language.
    assert MapPatternToEmitter().map("Gateway", _GO) == "go/ddd_clean/GatewayEmitter"
    assert MapPatternToEmitter().map("Gateway", _RUST) == "rust/ddd_clean/GatewayEmitter"
