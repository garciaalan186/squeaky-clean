"""ModuleSpec entity: immutable §Notation module declaration."""

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
        class_names = {c.name for c in self.classes}
        for cls in self.classes:
            for dep in cls.depends:
                if dep not in class_names:
                    violations.append(
                        f"{cls.name} depends on unknown class {dep}"
                    )
            for entry in cls.fields:
                if ":" not in entry:
                    violations.append(
                        f"{cls.name} field {entry!r} missing 'name: Type'"
                    )
        return violations
