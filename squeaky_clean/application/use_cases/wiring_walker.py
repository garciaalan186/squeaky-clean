"""wiring_walker: extract Adapters/UseCases + categorize them for WiringGenerator."""

from __future__ import annotations

from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

INBOUND_CATEGORIES: frozenset[str] = frozenset({
    "rest_server_handler", "grpc_server_handler",
    "websocket_server_handler", "message_queue_consumer",
})


def adapters(
    arch: ArchitectureSpec,
) -> tuple[tuple[ModuleSpec, ClassSpec], ...]:
    """Return Adapter classes from Infrastructure or Interface modules."""
    layers = (LayerType.INFRASTRUCTURE, LayerType.INTERFACE)
    return tuple((m, c) for m in arch.modules if m.layer in layers
                 for c in m.classes if c.pattern == "Adapter")


def use_cases(
    arch: ArchitectureSpec,
) -> tuple[tuple[ModuleSpec, ClassSpec], ...]:
    """Return Application-layer UseCase classes paired with their module."""
    return tuple((m, c) for m in arch.modules
                 if m.layer is LayerType.APPLICATION
                 for c in m.classes if c.pattern == "UseCase")


def category_for(cls: ClassSpec) -> str:
    """Infer the TechSpec category implied by ``cls.methods`` (or '')."""
    method_names = tuple(m.partition("(")[0].strip() for m in cls.methods)
    return infer_category(method_names) or ""


def env_args_for(spec: TechSpec | None) -> str:
    """Render a comma-separated arg list of os.environ.get(...) lookups."""
    if spec is None:
        return '""  # TODO: WiringGenerator missing TechSpec for this adapter'
    deps_raw = cast(list[str], spec.client_construction.get("dependencies") or [])
    parts = [f'os.environ.get("{d.upper()}", "")' for d in deps_raw]
    return ", ".join(parts) if parts else '""'


def first_with_category(
    adapters_in: tuple[tuple[ModuleSpec, ClassSpec], ...],
    category: str,
) -> ClassSpec | None:
    """Return the first Adapter classified as ``category`` (or None)."""
    for _m, c in adapters_in:
        if category_for(c) == category:
            return c
    return None


def split_inbound(
    adapters_in: tuple[tuple[ModuleSpec, ClassSpec], ...],
) -> tuple[
    list[tuple[ModuleSpec, ClassSpec]], list[tuple[ModuleSpec, ClassSpec]],
]:
    """Split adapters into (outbound, inbound) so ctors are ordered correctly."""
    outbound: list[tuple[ModuleSpec, ClassSpec]] = []
    inbound: list[tuple[ModuleSpec, ClassSpec]] = []
    for m, c in adapters_in:
        (inbound if category_for(c) in INBOUND_CATEGORIES
         else outbound).append((m, c))
    return outbound, inbound
