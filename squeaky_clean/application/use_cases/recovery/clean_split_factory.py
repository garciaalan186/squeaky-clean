"""CleanSplitFactory: build the Entity/Repository/Adapter triple for a class."""

from squeaky_clean.domain.entities.class_spec import ClassSpec


class CleanSplitFactory:
    """Produces the three Clean-Architecture classes a coupled class becomes.

    SKELETON generator: the Entity keeps the original members (which still
    need business-vs-persistence classification — the agentic follow-up),
    and the Repository/Adapter carry conventional ``save``/``find_by_id``
    stubs. The shape is correct — a pure Entity behind a Repository port
    with a framework Adapter — but the member split is left for review.
    """

    def entity(self, cls: ClassSpec) -> ClassSpec:
        """Return the pure Entity: the original class, re-typed, un-coupled."""
        return ClassSpec(
            name=cls.name, pattern="Entity", implements=None,
            methods=cls.methods, depends=cls.depends, concretes=cls.concretes,
            fields=cls.fields, invariants=cls.invariants,
        )

    def repository(self, cls: ClassSpec) -> ClassSpec:
        """Return the Repository port for the entity (same module)."""
        return ClassSpec(
            name=f"{cls.name}Repository", pattern="Repository", implements=None,
            methods=self._crud(cls), depends=(cls.name,), concretes=(),
            fields=(), invariants=(),
        )

    def adapter(self, cls: ClassSpec, module: str) -> ClassSpec:
        """Return the framework Adapter implementing the port (infra layer)."""
        return ClassSpec(
            name=f"{cls.name}Adapter", pattern="Adapter",
            implements=f"{cls.name}Repository", methods=self._crud(cls),
            depends=(f"{module}::{cls.name}", f"{module}::{cls.name}Repository"),
            concretes=(), fields=(), invariants=(),
        )

    def _crud(self, cls: ClassSpec) -> tuple[str, ...]:
        var = cls.name[:1].lower() + cls.name[1:]
        return (f"save({var}: {cls.name}): None", f"find_by_id(id: str): {cls.name}")
