"""ComposeEmitterSpec: template+delta emitter specs with per-language fallback."""

from squeaky_clean.application.generation.emission.composition.compose_agent_spec import (
    ComposeAgentSpec,
)
from squeaky_clean.application.generation.emission.composition.emitter_lang_block_filter import (
    EmitterLangBlockFilter,
)
from squeaky_clean.application.generation.emission.composition.emitter_profile import EmitterProfile
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


class ComposeEmitterSpec:
    """Resolves an emitter spec name to prompt text (R6.1a).

    Prefers the shared template ``emitters/_shared/<category>/<Name>.md``
    composed with the language profile ``emitters/_shared/profiles/<lang>.md``
    ({{profile:*}} blocks + {{#lang:..}} conditionals + toolkit placeholders).
    Falls back to the per-language copy while a pattern is not yet cut over.
    A template WITHOUT its language profile is an authoring error and raises
    (loud, per R6.8) instead of silently degrading.
    """

    def __init__(self, loader: LoadAgentSpec) -> None:
        self._loader: LoadAgentSpec = loader
        self._render: ComposeAgentSpec = ComposeAgentSpec(loader)
        self._langs: EmitterLangBlockFilter = EmitterLangBlockFilter()

    def load(self, spec_name: str, toolkit: LanguageToolkit) -> str:
        """Return the composed (or fallback per-language) spec text."""
        parts = spec_name.split("/")
        if len(parts) != 3:
            return self._loader.load(spec_name)
        try:
            template = self._loader.load(f"_shared/{parts[1]}/{parts[2]}")
        except FileNotFoundError:
            return self._loader.load(spec_name)
        language = toolkit.language.value
        profile = EmitterProfile.from_markdown(
            self._loader.load(f"_shared/profiles/{language}"),
        )
        text = self._langs.filter(template, language)
        return self._render.render(profile.substitute(text), toolkit)
