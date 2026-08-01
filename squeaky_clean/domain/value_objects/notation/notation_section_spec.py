"""NotationSectionSpec: one top-level §Notation section's grammar row."""

from dataclasses import dataclass
from typing import Literal

NotationKind = Literal[
    "scalar", "name_list", "method_list", "invariant_list", "classes"
]


@dataclass(frozen=True)
class NotationSectionSpec:
    """Grammar row for one top-level §Notation section (R6.1c).

    ``singleton`` sections keep their first occurrence when multi-MODULE
    text repeats a keyword; non-singleton bodies are merged. A required
    ``scalar`` must be present AND non-empty; a required ``classes``
    block need only be present.
    """

    name: str
    kind: NotationKind
    required: bool
    singleton: bool

    def missing_message(self) -> str:
        """Parse-error text when this required section is absent."""
        noun = "block" if self.kind == "classes" else "declaration"
        return f"missing {self.name} {noun}"

    def rejects(self, body: str | None) -> bool:
        """True if ``body`` fails this section's required-ness rule."""
        if not self.required:
            return False
        if body is None:
            return True
        return self.kind == "scalar" and not body
