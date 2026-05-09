"""ParseNotation: convert §Notation text into a ModuleSpec entity."""

from squeaky_clean.application.use_cases.notation_class_parser import NotationClassParser
from squeaky_clean.application.use_cases.notation_invariants_parser import (
    NotationInvariantsParser,
)
from squeaky_clean.application.use_cases.notation_list_splitter import NotationListSplitter
from squeaky_clean.application.use_cases.notation_section_extractor import (
    NotationSectionExtractor,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.domain.value_objects.layer_type import LayerType


class ParseNotation:
    """Parses §Notation text into an immutable ModuleSpec."""

    def __init__(self) -> None:
        self._sections: NotationSectionExtractor = NotationSectionExtractor()
        self._classes: NotationClassParser = NotationClassParser()
        self._splits: NotationListSplitter = NotationListSplitter()
        self._invars: NotationInvariantsParser = NotationInvariantsParser()

    def parse(self, text: str) -> ModuleSpec:
        """Return a ModuleSpec built from raw §Notation text."""
        sections = self._sections.extract(self._strip_fences(text))
        if "MODULE" not in sections or not sections["MODULE"]:
            raise NotationParseError("missing MODULE declaration")
        if "LAYER" not in sections or not sections["LAYER"]:
            raise NotationParseError("missing LAYER declaration")
        if "CLASSES" not in sections:
            raise NotationParseError("missing CLASSES block")
        return ModuleSpec(
            name=sections["MODULE"].strip(),
            layer=self._parse_layer(sections["LAYER"].strip()),
            exports=self._splits.plain_tuple(sections.get("EXPORTS", "")),
            depends=self._splits.plain_tuple(sections.get("DEPENDS", "")),
            classes=self._classes.parse(sections["CLASSES"]),
            invariants=self._invars.parse(sections.get("INVARIANTS", "")),
        )

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
