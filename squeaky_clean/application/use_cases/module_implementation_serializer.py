"""ModuleImplementationSerializer: round-trip ModuleImplementation tuples (G3)."""

from __future__ import annotations

import json
from typing import Any

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.architecture_spec_serializer import (
    ArchitectureSpecSerializer,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class ModuleImplementationSerializer:
    """Serialize/deserialize a tuple[ModuleImplementation, ...] to/from JSON."""

    def __init__(self) -> None:
        self._arch_ser: ArchitectureSpecSerializer = ArchitectureSpecSerializer()

    def serialize(self, impls: tuple[ModuleImplementation, ...]) -> str:
        """Return JSON capturing each ModuleImplementation as a flat dict."""
        return json.dumps([self._to_dict(i) for i in impls], indent=2)

    def deserialize(self, payload: str) -> tuple[ModuleImplementation, ...]:
        """Parse JSON ``payload`` back into a tuple of ModuleImplementations."""
        data: list[dict[str, Any]] = json.loads(payload)
        return tuple(self._from_dict(d) for d in data)

    def _to_dict(self, impl: ModuleImplementation) -> dict[str, Any]:
        mod_payload = self._arch_ser._mod_to_dict(impl.module)  # noqa: SLF001
        return {
            "module": mod_payload,
            "implemented_classes": [self._ic_to_dict(ic)
                                    for ic in impl.implemented_classes],
            "total_cost_usd": impl.total_cost_usd,
            "total_duration_ms": impl.total_duration_ms,
            "total_input_tokens": impl.total_input_tokens,
            "total_output_tokens": impl.total_output_tokens,
            "wall_duration_ms": impl.wall_duration_ms,
            "total_retries": impl.total_retries,
        }

    def _ic_to_dict(self, ic: ImplementedClass) -> dict[str, Any]:
        return {
            "class_name": ic.class_name, "file_path": ic.file_path,
            "code": ic.code, "test_code": ic.test_code,
            "cost_usd": ic.cost_usd, "duration_ms": ic.duration_ms,
            "input_tokens": ic.input_tokens, "output_tokens": ic.output_tokens,
            "retries": ic.retries,
        }

    def _from_dict(self, d: dict[str, Any]) -> ModuleImplementation:
        module: ModuleSpec = self._arch_ser._mod_from_dict(d["module"])  # noqa: SLF001
        ics = tuple(self._ic_from_dict(c) for c in d["implemented_classes"])
        return ModuleImplementation(
            module=module, implemented_classes=ics,
            total_cost_usd=d["total_cost_usd"],
            total_duration_ms=d["total_duration_ms"],
            total_input_tokens=d["total_input_tokens"],
            total_output_tokens=d["total_output_tokens"],
            wall_duration_ms=d["wall_duration_ms"],
            total_retries=d.get("total_retries", 0),
        )

    def _ic_from_dict(self, d: dict[str, Any]) -> ImplementedClass:
        return ImplementedClass(
            class_name=d["class_name"], file_path=d["file_path"],
            code=d["code"], test_code=d["test_code"],
            cost_usd=d["cost_usd"], duration_ms=d["duration_ms"],
            input_tokens=d["input_tokens"], output_tokens=d["output_tokens"],
            retries=d.get("retries", 0),
        )
