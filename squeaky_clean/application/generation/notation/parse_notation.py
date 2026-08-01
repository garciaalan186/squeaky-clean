"""ParseNotation: convert §Notation text into a ModuleSpec entity."""

from squeaky_clean.application.generation.notation.notation_class_parser import NotationClassParser
from squeaky_clean.application.generation.notation.notation_field_value_parser import (
    NotationFieldValueParser,
)
from squeaky_clean.application.generation.notation.notation_section_extractor import (
    NotationSectionExtractor,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.notation.notation_schema import SQUIB_SCHEMA


class ParseNotation:
    """Parses §Notation text into an immutable ModuleSpec.

    Required-section rules and list-section kinds come from SQUIB_SCHEMA
    (R6.1c) — this class only orchestrates.
    """

    def __init__(self) -> None:
        self._sections: NotationSectionExtractor = NotationSectionExtractor()
        self._classes: NotationClassParser = NotationClassParser()
        self._values: NotationFieldValueParser = NotationFieldValueParser()

    def parse(self, text: str) -> ModuleSpec:
        """Return a ModuleSpec built from raw §Notation text."""
        sections = self._sections.extract(self._strip_fences(text))
        for spec in SQUIB_SCHEMA.required_sections():
            if spec.rejects(sections.get(spec.name)):
                raise NotationParseError(spec.missing_message())
        return ModuleSpec(
            name=sections["MODULE"].strip(),
            layer=self._parse_layer(sections["LAYER"].strip()),
            exports=self._list_section(sections, "EXPORTS"),
            depends=self._list_section(sections, "DEPENDS"),
            classes=self._classes.parse(sections["CLASSES"]),
            invariants=self._list_section(sections, "INVARIANTS"),
        )

    def _list_section(
        self, sections: dict[str, str], name: str
    ) -> tuple[str, ...]:
        kind = SQUIB_SCHEMA.section(name).kind
        return self._values.sequence(sections.get(name, ""), kind)

    def _parse_layer(self, raw: str) -> LayerType:
        try:
            return LayerType(raw.lower())
        except ValueError as exc:
            raise NotationParseError(f"unknown layer: {raw!r}") from exc

    def _strip_fences(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return stripped
