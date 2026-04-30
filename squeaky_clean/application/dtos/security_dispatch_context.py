"""SecurityDispatchContext DTO: inputs for SecurityICPDispatcher."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class SecurityDispatchContext:
    """Immutable bundle of SecurityReview + ModuleSpec + LanguageToolkit.

    Groups inputs for SecurityICPDispatcher.dispatch so it stays within
    the <=2-args rule. ``architecture`` is optional — when supplied the
    formatter can resolve a dependency's owner module to compute the
    correct dotted-path import.
    """

    review: SecurityReview
    module: ModuleSpec
    toolkit: LanguageToolkit
    architecture: ArchitectureSpec | None = None
