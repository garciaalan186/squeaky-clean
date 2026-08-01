"""RuleRunnerFactory: assembles the per-language architectural rule set."""

from squeaky_clean.application.generation.validation.rule_runner import RuleRunner
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.rules.dependency_rule import DependencyRule
from squeaky_clean.domain.rules.pattern_conformance import PatternConformanceRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapter_bundle import LanguageAdapterBundle


class RuleRunnerFactory:
    """Builds the RuleRunner for a language's adapter bundle."""

    def build(
        self, adapters: LanguageAdapterBundle, toolkit: LanguageToolkit,
    ) -> RuleRunner:
        """Return a RuleRunner over the rules applicable to ``toolkit``."""
        rules: tuple[Rule, ...] = (adapters.granularity_rule,)
        if toolkit.language is TargetLanguage.PYTHON:
            rules = (
                adapters.granularity_rule,
                DependencyRule(),
                PatternConformanceRule(),
            )
        return RuleRunner(rules, toolkit.file_extension)
