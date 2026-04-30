"""ClassSpec entity: immutable description of one class within a ModuleSpec."""

from dataclasses import dataclass, field

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
