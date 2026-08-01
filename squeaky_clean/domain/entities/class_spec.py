"""ClassSpec entity: immutable description of one class within a ModuleSpec."""

from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field

from squeaky_clean.domain.value_objects.class_role import ClassRole
from squeaky_clean.domain.value_objects.pattern_name import PatternName


@dataclass(frozen=True)
class ClassSpec:
    """One class declared by a ModuleSpec in §Notation form.

    Fields follow §Notation: `name` is the class identifier, `pattern`
    is a PatternName literal, `implements` is an optional interface,
    `fields` declares constructor-required state (`name: Type` strings),
    `methods` are `methodName(argType: ArgType): ReturnType` strings,
    `depends` lists sibling classes, and `concretes` lists polymorphic
    variants for an abstract pattern (Strategy, State, Visitor, ...).
    """

    name: str
    pattern: PatternName
    implements: str | None
    methods: tuple[str, ...]
    depends: tuple[str, ...]
    concretes: tuple[str, ...]
    fields: tuple[str, ...] = field(default_factory=tuple)
    invariants: tuple[str, ...] = field(default_factory=tuple)

    def role(self) -> ClassRole:
        """Polymorphic role: ABSTRACT if concretes declared, CONCRETE if
        an implements target is set, PLAIN otherwise."""
        if self.concretes:
            return ClassRole.ABSTRACT
        if self.implements:
            return ClassRole.CONCRETE
        return ClassRole.PLAIN

    def unknown_dep_violations(self, resolvable: AbstractSet[str]) -> list[str]:
        """One violation per §Notation dep whose bare name is unresolvable.

        Qualified ``Module::Type`` deps are checked by their bare type name;
        the violation string always quotes the dep as declared.
        """
        out: list[str] = []
        for dep in self.depends:
            bare = dep.split("::", 1)[1] if "::" in dep else dep
            if bare not in resolvable:
                out.append(f"{self.name} depends on unknown class {dep}")
        return out

    def field_syntax_violations(self) -> list[str]:
        """One violation per fields entry missing the `name: Type` shape."""
        return [
            f"{self.name} field {entry!r} missing 'name: Type'"
            for entry in self.fields
            if ":" not in entry
        ]
