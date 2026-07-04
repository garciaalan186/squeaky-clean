"""SquibEmitter: render an ArchitectureSpec as reviewable Squib text."""

from squeaky_clean.application.use_cases.recovery.squib_module_writer import (
    SquibModuleWriter,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class SquibEmitter:
    """Serializes a full ArchitectureSpec into Squib (§Notation) text.

    This is the inverse of ParseArchitectureNotation and the piece the
    greenfield path never needed: Architecture Recovery emits it so a
    human can read and edit the recovered architecture before regeneration.
    Modules are rendered in order and separated by a blank line, matching
    the multi-module layout the parser splits on. The output round-trips:
    ``parse(emit(spec))`` reproduces ``spec``'s modules.
    """

    def __init__(self) -> None:
        self._module: SquibModuleWriter = SquibModuleWriter()

    def emit(self, spec: ArchitectureSpec) -> str:
        """Return the Squib text for every module in the architecture."""
        return "\n\n".join(self._module.write(m) for m in spec.modules) + "\n"
