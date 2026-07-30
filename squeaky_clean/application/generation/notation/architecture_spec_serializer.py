"""ArchitectureSpecSerializer: round-trip ArchitectureSpec through JSON (G3)."""

from __future__ import annotations

import json
from typing import Any, cast

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class ArchitectureSpecSerializer:
    """Serialize/deserialize ArchitectureSpec to/from a JSON string."""

    def serialize(self, spec: ArchitectureSpec) -> str:
        """Return JSON string capturing every module/class field."""
        modules = [self._mod_to_dict(m) for m in spec.modules]
        edges = {k: list(v) for k, v in spec.graph.edges.items()}
        return json.dumps({"modules": modules, "edges": edges}, indent=2)

    def deserialize(self, payload: str) -> ArchitectureSpec:
        """Parse JSON ``payload`` back into an ArchitectureSpec."""
        data: dict[str, Any] = json.loads(payload)
        modules = tuple(self._mod_from_dict(m) for m in data["modules"])
        edges = {k: tuple(v) for k, v in data["edges"].items()}
        return ArchitectureSpec(
            modules=modules, graph=ArchitectureGraph(edges=edges),
        )

    def _mod_to_dict(self, m: ModuleSpec) -> dict[str, Any]:
        return {
            "name": m.name, "layer": m.layer.value,
            "exports": list(m.exports), "depends": list(m.depends),
            "classes": [self._cls_to_dict(c) for c in m.classes],
            "invariants": list(m.invariants),
        }

    def _cls_to_dict(self, c: ClassSpec) -> dict[str, Any]:
        return {
            "name": c.name, "pattern": c.pattern,
            "implements": c.implements, "methods": list(c.methods),
            "depends": list(c.depends), "concretes": list(c.concretes),
            "fields": list(c.fields), "invariants": list(c.invariants),
        }

    def _mod_from_dict(self, d: dict[str, Any]) -> ModuleSpec:
        return ModuleSpec(
            name=d["name"], layer=LayerType(d["layer"]),
            exports=tuple(d["exports"]), depends=tuple(d["depends"]),
            classes=tuple(self._cls_from_dict(c) for c in d["classes"]),
            invariants=tuple(d["invariants"]),
        )

    def _cls_from_dict(self, d: dict[str, Any]) -> ClassSpec:
        return ClassSpec(
            name=d["name"], pattern=cast(PatternName, d["pattern"]),
            implements=d["implements"], methods=tuple(d["methods"]),
            depends=tuple(d["depends"]), concretes=tuple(d["concretes"]),
            fields=tuple(d["fields"]), invariants=tuple(d["invariants"]),
        )
