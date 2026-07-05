"""SquibClassWriter: render one ClassSpec as a Squib class block."""

from squeaky_clean.domain.entities.class_spec import ClassSpec


class SquibClassWriter:
    """Serializes a ClassSpec into the `Name -> Pattern { ... }` block.

    `fields` and `methods` are always emitted (possibly empty lists) so the
    output satisfies the grammar's required sub-fields; `implements`,
    `depends`, `concretes`, and `invariants` are emitted only when present.
    The result parses back through NotationClassParser unchanged — this is
    the inverse of the class-block parser used on the greenfield path.
    """

    def write(self, cls: ClassSpec) -> str:
        """Return the indented Squib block for one class."""
        lines = [f"  {cls.name} -> {cls.pattern} {{"]
        if cls.implements:
            lines.append(f"    implements: {cls.implements}")
        lines.append(f"    fields: [{', '.join(cls.fields)}]")
        lines.append(f"    methods: [{', '.join(cls.methods)}]")
        for key, values in self._optional(cls):
            if values:
                lines.append(f"    {key}: [{', '.join(values)}]")
        lines.append("  }")
        return "\n".join(lines)

    def _optional(self, cls: ClassSpec) -> tuple[tuple[str, tuple[str, ...]], ...]:
        return (
            ("depends", cls.depends),
            ("concretes", cls.concretes),
            ("invariants", cls.invariants),
        )
