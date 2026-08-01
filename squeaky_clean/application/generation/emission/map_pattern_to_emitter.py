"""MapPatternToEmitter: resolve a §Notation PatternName to an ICP spec path."""

from squeaky_clean.application.generation.emission.routing.pattern_category_table import (
    FALLBACK_CATEGORY,
    FALLBACK_NAME,
    PATTERN_CATEGORY,
)
from squeaky_clean.application.generation.emission.routing.tier_c_router import TierCRouter
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

# R6.10: languages with a live emitter spec fleet on the loader search path.
# Go/Rust fleets are ARCHIVED under interface/agent_specs/_attic/emitters/
# until a real Go/Rust problem funds them (their P0 toys were never run in
# CI). Single source of truth — spec-existence tests parametrize over this,
# NOT over the full TargetLanguage enum.
ACTIVE_EMITTER_LANGUAGES: tuple[TargetLanguage, ...] = (
    TargetLanguage.PYTHON,
    TargetLanguage.JAVASCRIPT,
    TargetLanguage.TYPESCRIPT,
    TargetLanguage.JAVA,
)


class MapPatternToEmitter:
    """Maps a pattern name to the slash-qualified ICP spec path to load."""

    def __init__(
        self, toolkit: LanguageToolkit, infrastructure_mode: str = "manual",
    ) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._infra_mode: str = infrastructure_mode
        self._tier_c: TierCRouter = TierCRouter()

    def register_category(self, category: str) -> None:
        """Record a declared Tier C category (ProblemSpec order preserved)."""
        self._tier_c.register_category(category)

    def map(self, pattern: str) -> str:
        """Return ``<lang>/<category>/<Pattern>Emitter`` for any catalog pattern.

        Only a genuinely unrecognized pattern name falls back to
        ``<lang>/ddd_clean/SimpleClassEmitter``. ``pattern`` is deliberately
        `str`, not PatternName: this boundary accepts out-of-catalog names
        (custom patterns, hallucinated names) and routes them to the escape
        hatch instead of crashing.
        """
        library = self._toolkit.icp_library
        category = PATTERN_CATEGORY.get(pattern)
        if category is not None:
            return f"{library}/{category}/{pattern}Emitter"
        return f"{library}/{FALLBACK_CATEGORY}/{FALLBACK_NAME}"

    def map_for(self, cls: ClassSpec, module: ModuleSpec) -> str:
        """Return the Tier C path for Infrastructure/Interface-layer
        Repository/Gateway/Adapter classes when ``--infra=auto`` (H5a/H5b via
        TierCRouter); every other input takes the catalog ``map`` route.
        """
        if self._infra_mode == "auto":
            icp = self._tier_c.route(cls, module)
            if icp is not None:
                return f"{self._toolkit.icp_library}/infrastructure/{icp}"
        return self.map(cls.pattern)
