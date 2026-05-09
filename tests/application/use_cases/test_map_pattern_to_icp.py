"""Tests for MapPatternToICP."""

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.map_pattern_to_icp import MapPatternToICP
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
_GO = LanguageToolkitFactory().for_language(TargetLanguage.GO)
_RUST = LanguageToolkitFactory().for_language(TargetLanguage.RUST)


def test_strategy_maps_to_python_strategy_icp() -> None:
    assert MapPatternToICP().map("Strategy", _PY) == "python/behavioral/StrategyICP"


def test_entity_maps_to_python_entity_icp() -> None:
    assert MapPatternToICP().map("Entity", _PY) == "python/ddd_clean/EntityICP"


def test_value_object_maps_to_python_value_object_icp() -> None:
    assert (
        MapPatternToICP().map("ValueObject", _PY)
        == "python/ddd_clean/ValueObjectICP"
    )


def test_simple_class_maps_to_python_simple_class_icp() -> None:
    assert (
        MapPatternToICP().map("SimpleClass", _PY)
        == "python/ddd_clean/SimpleClassICP"
    )


def test_unknown_pattern_falls_back_to_simple_class() -> None:
    assert (
        MapPatternToICP().map("Facade", _PY)
        == "python/ddd_clean/SimpleClassICP"
    )
    assert (
        MapPatternToICP().map("Observer", _PY)
        == "python/ddd_clean/SimpleClassICP"
    )


def test_entity_maps_to_go_entity_icp() -> None:
    assert MapPatternToICP().map("Entity", _GO) == "go/ddd_clean/EntityICP"


def test_value_object_maps_to_go_value_object_icp() -> None:
    assert (
        MapPatternToICP().map("ValueObject", _GO)
        == "go/ddd_clean/ValueObjectICP"
    )


def test_strategy_maps_to_go_strategy_icp() -> None:
    assert MapPatternToICP().map("Strategy", _GO) == "go/behavioral/StrategyICP"


def test_simple_class_maps_to_go_simple_class_icp() -> None:
    assert (
        MapPatternToICP().map("SimpleClass", _GO)
        == "go/ddd_clean/SimpleClassICP"
    )


def test_entity_maps_to_rust_entity_icp() -> None:
    assert MapPatternToICP().map("Entity", _RUST) == "rust/ddd_clean/EntityICP"


def test_value_object_maps_to_rust_value_object_icp() -> None:
    assert (
        MapPatternToICP().map("ValueObject", _RUST)
        == "rust/ddd_clean/ValueObjectICP"
    )


def test_strategy_maps_to_rust_strategy_icp() -> None:
    assert (
        MapPatternToICP().map("Strategy", _RUST)
        == "rust/behavioral/StrategyICP"
    )


def test_simple_class_maps_to_rust_simple_class_icp() -> None:
    assert (
        MapPatternToICP().map("SimpleClass", _RUST)
        == "rust/ddd_clean/SimpleClassICP"
    )


def test_repository_in_infrastructure_with_blob_methods_routes_tier_c() -> None:
    """H1 — Repository on Infrastructure layer with put_blob/get_blob/delete_blob
    routes to BlobStorageAdapterICP when --infra=auto."""
    icp = MapPatternToICP().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/BlobStorageAdapterICP"


def test_repository_falls_back_when_infra_mode_manual() -> None:
    """Backwards compatibility: --infra=manual disables the Tier C path."""
    icp = MapPatternToICP().map_with_layer(
        "Repository", _PY, LayerType.INFRASTRUCTURE,
        ("put_blob", "get_blob", "delete_blob"),
        infrastructure_mode="manual",
    )
    assert icp == "python/ddd_clean/SimpleClassICP"


def test_repository_in_domain_layer_never_routes_tier_c() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Repository", _PY, LayerType.DOMAIN,
        ("put_blob", "get_blob"),
        infrastructure_mode="auto",
    )
    assert icp == "python/ddd_clean/SimpleClassICP"
