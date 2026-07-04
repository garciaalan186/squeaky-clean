"""SquibModuleWriter: render one ModuleSpec as a Squib MODULE block."""

from squeaky_clean.application.use_cases.recovery.squib_class_writer import (
    SquibClassWriter,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class SquibModuleWriter:
    """Serializes a ModuleSpec into a full `MODULE ... INVARIANTS` block.

    The LAYER token is capitalized (``Domain``) to match the grammar; the
    parser lowercases it on the way back. EXPORTS, DEPENDS, and INVARIANTS
    are always present (possibly empty) per the required-section rules.
    Classes are delegated to SquibClassWriter.
    """

    def __init__(self) -> None:
        self._classes: SquibClassWriter = SquibClassWriter()

    def write(self, module: ModuleSpec) -> str:
        """Return the full Squib text for one module."""
        lines = [
            f"MODULE {module.name}",
            f"LAYER {module.layer.value.capitalize()}",
            f"EXPORTS [{', '.join(module.exports)}]",
            f"DEPENDS [{', '.join(module.depends)}]",
            "CLASSES {",
        ]
        lines.extend(self._classes.write(cls) for cls in module.classes)
        lines.append("}")
        lines.append(f"INVARIANTS [{', '.join(module.invariants)}]")
        return "\n".join(lines)
