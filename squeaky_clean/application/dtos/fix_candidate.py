"""FixCandidate DTO: one class whose tests failed, queued for a fixer ICP."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.class_spec import ClassSpec


@dataclass(frozen=True)
class FixCandidate:
    """Bundle passed to one fixer LLM call.

    `original` is the ImplementedClass that failed tests. `class_spec`
    is the ClassSpec from the originating ModuleSpec so the fixer can
    re-check signatures. `failure_excerpt` is the relevant slice of
    raw test output to aid diagnosis. `toolkit` carries language
    conventions for the regen prompt.
    """

    original: ImplementedClass
    class_spec: ClassSpec
    failure_excerpt: str
    toolkit: LanguageToolkit
    # SIBLING_INTERFACES block (names, methods, import paths of collaborators)
    # so the fixer can resolve cross-file imports and interface conformance.
    sibling_context: str = ""
