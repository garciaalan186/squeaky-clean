"""ModuleSpec entity: immutable §Notation module declaration."""

from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


@dataclass(frozen=True)
class ModuleSpec:
    """One §Notation MODULE block. Frozen so it is safe to share."""

    name: str
    layer: LayerType
    exports: tuple[str, ...]
    depends: tuple[str, ...]
    classes: tuple[ClassSpec, ...]
    invariants: tuple[str, ...]

    def validate(self) -> list[str]:
        """Return list of structural-integrity violations (empty = valid).

        Checks structural invariants only (name exists, classes exist,
        depends references resolve, field syntax). Does NOT enforce
        numeric thresholds (method count, arg count) — those are
        tracked as soft metrics by the granularity rules.
        """
        violations: list[str] = []
        if not self.name:
            violations.append("module name is empty")
        if not self.classes:
            violations.append("module declares zero classes")
        violations.extend(self.unknown_dep_violations(frozenset()))
        violations.extend(self.field_syntax_violations())
        return violations

    def unknown_dep_violations(self, external: AbstractSet[str]) -> list[str]:
        """Class deps unresolvable against local classes ∪ ``external``.

        ``external`` carries the names resolvable beyond this module
        (e.g. classes exported by sibling modules); pass an empty set
        for standalone single-module validation.
        """
        resolvable = {c.name for c in self.classes} | set(external)
        out: list[str] = []
        for cls in self.classes:
            out.extend(cls.unknown_dep_violations(resolvable))
        return out

    def field_syntax_violations(self) -> list[str]:
        """Malformed `name: Type` fields entries across all classes."""
        out: list[str] = []
        for cls in self.classes:
            out.extend(cls.field_syntax_violations())
        return out
