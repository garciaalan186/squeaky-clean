"""Tests for TierCRouter (verb heuristic + declared-category fallback)."""

from squeaky_clean.application.generation.emission.routing.tier_c_router import TierCRouter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def _pair(
    pattern: PatternName, layer: LayerType, methods: tuple[str, ...],
) -> tuple[ClassSpec, ModuleSpec]:
    cls = ClassSpec(
        name="Subject", pattern=pattern, implements=None,
        methods=methods, depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="M", layer=layer, exports=(), depends=(),
        classes=(cls,), invariants=(),
    )
    return cls, module


def test_verb_heuristic_routes_blob_storage() -> None:
    cls, module = _pair(
        "Repository", LayerType.INFRASTRUCTURE, ("put_blob", "get_blob"),
    )
    assert TierCRouter().route(cls, module) == "BlobStorageAdapterEmitter"


def test_non_infra_pattern_is_outside_the_gate() -> None:
    cls, module = _pair("Entity", LayerType.INFRASTRUCTURE, ("put_blob",))
    assert TierCRouter().route(cls, module) is None


def test_domain_layer_is_outside_the_gate() -> None:
    cls, module = _pair("Repository", LayerType.DOMAIN, ("put_blob",))
    assert TierCRouter().route(cls, module) is None


def test_declared_category_wins_when_verbs_are_ambiguous() -> None:
    cls, module = _pair("Repository", LayerType.INFRASTRUCTURE, ("frobnicate",))
    router = TierCRouter()
    router.register_category("kv_cache")
    assert router.route(cls, module) == "KvCacheEmitter"


def test_declared_interface_category_is_layer_checked() -> None:
    # An inbound-handler category may not be routed into INFRASTRUCTURE.
    cls, module = _pair("Adapter", LayerType.INFRASTRUCTURE, ("frobnicate",))
    router = TierCRouter()
    router.register_category("rest_server_handler")
    assert router.route(cls, module) is None
