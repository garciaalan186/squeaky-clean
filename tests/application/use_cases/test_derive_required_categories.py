"""Tests for derive_required_categories (H3)."""

from squeaky_clean.application.use_cases.derive_required_categories import (
    derive_required_categories,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(layer: LayerType, classes: tuple[ClassSpec, ...]) -> ModuleSpec:
    return ModuleSpec(
        name="M", layer=layer, exports=(), depends=(),
        classes=classes, invariants=(),
    )


def _arch(*modules: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(modules=tuple(modules), graph=ArchitectureGraph(edges={}))


def _cls(name: str, methods: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="Adapter", implements=None,
        methods=methods, depends=(), concretes=(),
    )


def test_blob_storage_inferred_from_put_get_blob() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("S3Adapter", ("put_blob(key: str, body: bytes): None",
                           "get_blob(key: str): bytes")),
    )))
    assert derive_required_categories(arch) == frozenset({"blob_storage"})


def test_kv_cache_inferred_from_set_get_expire() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("Cache", ("set(k: str, v: bytes): None",
                       "get(k: str): bytes",
                       "expire(k: str, ttl: int): None")),
    )))
    assert derive_required_categories(arch) == frozenset({"kv_cache"})


def test_rest_client_inferred_from_request_post() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("Http", ("request(method: str, url: str): Response",
                      "post(url: str, body: bytes): Response",
                      "get(url: str): Response")),
    )))
    assert derive_required_categories(arch) == frozenset({"rest_client"})


def test_domain_module_ignored() -> None:
    arch = _arch(_module(LayerType.DOMAIN, (
        _cls("Order", ("validate(): bool",)),
    )))
    assert derive_required_categories(arch) == frozenset()
