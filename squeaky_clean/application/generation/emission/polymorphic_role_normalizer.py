"""PolymorphicRoleNormalizer: derive implements/concretes for pattern families."""

from dataclasses import replace

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec

# Patterns whose participants split into one abstract base + polymorphic
# concretes (§Notation `concretes:`). Same-pattern `depends:` edges between
# two such classes always mean concrete -> abstract.
_POLYMORPHIC: frozenset[str] = frozenset({
    "Strategy", "State", "Visitor", "Observer", "Command",
    "TemplateMethod", "ChainOfResponsibility",
})


class PolymorphicRoleNormalizer:
    """Stamps abstract/concrete roles the architect left implicit.

    Architects emit two equivalent Squib shapes for e.g. Strategy: the
    canonical `Abstract { concretes: [A, B] }`, or three peer classes where
    each concrete declares `depends: [Abstract]`. Emitter specs key on
    `implements`/`concretes` ("concretes non-empty => emit the interface"),
    so the second shape used to produce a CONCRETE abstract participant
    (P2JAVA "interface expected here", R0.11). This pure pre-dispatch pass
    translates the depends shape into the fields the emitters key on.
    """

    def normalize(self, module: ModuleSpec) -> ModuleSpec:
        """Return ``module`` with implements/concretes derived from depends."""
        by_name = {c.name: c for c in module.classes}
        implements: dict[str, str] = {}
        concretes: dict[str, list[str]] = {}
        for cls in module.classes:
            base = self._base_of(cls, by_name)
            if base is not None:
                implements[cls.name] = base
                concretes.setdefault(base, []).append(cls.name)
            # implements-driven (pattern-agnostic): a declared `implements:`
            # target IS an abstract participant — stamp its concretes so the
            # target's emitter renders an interface, whatever its pattern
            # (e.g. an Adapter's port declared as SimpleClass — java
            # "interface expected here", R5.6 micro-eval finding).
            elif cls.implements and cls.implements in by_name:
                concretes.setdefault(cls.implements, []).append(cls.name)
        if not implements and not concretes:
            return module
        classes = tuple(
            self._stamp(c, implements, concretes) for c in module.classes
        )
        return replace(module, classes=classes)

    @staticmethod
    def _base_of(cls: ClassSpec, by_name: dict[str, ClassSpec]) -> str | None:
        if cls.pattern not in _POLYMORPHIC or cls.implements:
            return None
        for dep in cls.depends:
            target = by_name.get(dep)
            if target is not None and target.pattern == cls.pattern:
                return dep
        return None

    @staticmethod
    def _stamp(
        cls: ClassSpec,
        implements: dict[str, str],
        concretes: dict[str, list[str]],
    ) -> ClassSpec:
        derived = concretes.get(cls.name, [])
        merged = cls.concretes + tuple(
            n for n in derived if n not in cls.concretes
        )
        impl = cls.implements or implements.get(cls.name)
        if merged == cls.concretes and impl == cls.implements:
            return cls
        return replace(cls, implements=impl, concretes=merged)
