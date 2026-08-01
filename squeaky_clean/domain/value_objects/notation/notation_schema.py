"""NotationSchema: the §Notation grammar as data (R6.1c)."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.notation.notation_class_field_spec import (
    NotationClassFieldSpec,
)
from squeaky_clean.domain.value_objects.notation.notation_section_spec import NotationSectionSpec


@dataclass(frozen=True)
class NotationSchema:
    """Single source of truth for §Notation's shape.

    Consumed by the notation parser fleet (section splitting, required
    checks, field-kind dispatch) and by the R5.5 shape classifier (the
    novelty-signature bit order), so the grammar lives here instead of
    as folklore spread across parser modules and docs/squib.md.
    """

    sections: tuple[NotationSectionSpec, ...]
    class_fields: tuple[NotationClassFieldSpec, ...]

    def singleton_sections(self) -> frozenset[str]:
        """Names of sections whose first occurrence wins on duplicates."""
        return frozenset(s.name for s in self.sections if s.singleton)

    def required_sections(self) -> tuple[NotationSectionSpec, ...]:
        """Sections a module block cannot omit, in declaration order."""
        return tuple(s for s in self.sections if s.required)

    def section(self, name: str) -> NotationSectionSpec:
        """The grammar row for one section name (KeyError if unknown)."""
        for section in self.sections:
            if section.name == name:
                return section
        raise KeyError(name)

    def class_field_names(self) -> tuple[str, ...]:
        """Class-entry field names in canonical shape-signature order."""
        return tuple(f.name for f in self.class_fields)

    def class_field(self, name: str) -> NotationClassFieldSpec:
        """The grammar row for one class field name (KeyError if unknown)."""
        for class_field in self.class_fields:
            if class_field.name == name:
                return class_field
        raise KeyError(name)


SQUIB_SCHEMA = NotationSchema(
    sections=(
        NotationSectionSpec("MODULE", "scalar", required=True, singleton=True),
        NotationSectionSpec("LAYER", "scalar", required=True, singleton=True),
        NotationSectionSpec("EXPORTS", "name_list", required=False, singleton=False),
        NotationSectionSpec("DEPENDS", "name_list", required=False, singleton=False),
        NotationSectionSpec("CLASSES", "classes", required=True, singleton=False),
        NotationSectionSpec(
            "INVARIANTS", "invariant_list", required=False, singleton=False
        ),
    ),
    # Class-field order IS the R5.5 shape-signature bit order — keep stable
    # so novelty signatures stay comparable across runs and triage snapshots.
    class_fields=(
        NotationClassFieldSpec("fields", "name_list"),
        NotationClassFieldSpec("methods", "method_list"),
        NotationClassFieldSpec("depends", "name_list"),
        NotationClassFieldSpec("concretes", "name_list"),
        NotationClassFieldSpec("implements", "scalar"),
        NotationClassFieldSpec("invariants", "invariant_list"),
    ),
)
