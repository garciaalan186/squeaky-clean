"""ComposeAgentSpec: render a shared-spec template against a LanguageToolkit."""

from __future__ import annotations

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec


class ComposeAgentSpec:
    """Loads an agent spec and substitutes language-specific placeholders.

    Placeholders use double-brace form ``{{name}}`` so they don't collide
    with markdown's curly-brace prose. Substitution targets:
      ``{{file_extension}}``, ``{{test_file_prefix}}``, ``{{test_file_suffix}}``,
      ``{{identifier_case}}``, ``{{test_framework_imports}}``,
      ``{{error_types_tuple}}``, ``{{assert_eq_template}}``,
      ``{{assert_raises_template}}``, ``{{array_type_template}}``,
      ``{{method_signature_style}}``, ``{{language}}``.
    Unknown placeholders are left literal so agents can introspect them.
    """

    def __init__(self, loader: LoadAgentSpec | None = None) -> None:
        self._loader: LoadAgentSpec = loader or LoadAgentSpec()

    def compose(self, spec_name: str, toolkit: LanguageToolkit) -> str:
        """Return the spec's text with language placeholders substituted."""
        template = self._loader.load(spec_name)
        return self._substitute(template, toolkit)

    def _substitute(self, text: str, t: LanguageToolkit) -> str:
        mapping: dict[str, str] = {
            "{{file_extension}}": t.file_extension,
            "{{test_file_prefix}}": t.test_file_prefix,
            "{{test_file_suffix}}": t.test_file_suffix,
            "{{identifier_case}}": t.identifier_case,
            "{{test_framework_imports}}": t.test_framework_imports,
            "{{error_types_tuple}}": t.error_types_tuple,
            "{{assert_eq_template}}": t.assert_eq_template,
            "{{assert_raises_template}}": t.assert_raises_template,
            "{{array_type_template}}": t.array_type_template,
            "{{method_signature_style}}": t.method_signature_style,
            "{{language}}": t.language.value,
        }
        out = text
        for placeholder, value in mapping.items():
            out = out.replace(placeholder, value)
        return out
