"""ClassAssignmentFormatter: serialize a ClassAssignment into a user prompt."""

from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.application.generation.emission.sibling_interface_formatter import (
    SiblingInterfaceFormatter,
)
from squeaky_clean.application.generation.techspec.tech_spec_block_formatter import (
    TechSpecBlockFormatter,
)
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


class ClassAssignmentFormatter:
    """Turns a ClassAssignment into the user prompt text an ICP consumes."""

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._tech: TechSpecBlockFormatter = TechSpecBlockFormatter()

    def format(self, assignment: ClassAssignment) -> str:
        """Return a declarative block describing the class to implement."""
        spec = assignment.class_spec
        fields = ", ".join(spec.fields) if spec.fields else ""
        methods = ", ".join(spec.methods) if spec.methods else ""
        depends = ", ".join(spec.depends) if spec.depends else ""
        concretes = ", ".join(spec.concretes) if spec.concretes else ""
        implements = spec.implements or ""
        siblings = SiblingInterfaceFormatter(
            self._toolkit, assignment.architecture,
        ).format(assignment.module, spec)
        lines: list[str] = [
            f"CLASS {spec.name}",
            f"PATTERN {spec.pattern}",
            f"IMPLEMENTS {implements}",
            f"FIELDS [{fields}]",
            f"METHODS [{methods}]",
            f"DEPENDS [{depends}]",
            f"CONCRETES [{concretes}]",
        ]
        if spec.invariants:
            quoted = ", ".join(f'"{inv}"' for inv in spec.invariants)
            lines.append(f"INVARIANTS [{quoted}]")
        lines.append(f"FILE_PATH {assignment.file_path}")
        lines.append(siblings)
        if assignment.tech_spec is not None:
            lines.append(self._tech.format(assignment.tech_spec))
        return "\n".join(lines)
