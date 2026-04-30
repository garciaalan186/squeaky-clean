"""K9: registry coverage — every TargetLanguage must have a registered factory."""

import pytest

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY
from squeaky_clean.interface.cli.language_adapter_selector import _INSTALLERS


@pytest.mark.parametrize("language", list(TargetLanguage))
def test_every_target_language_has_a_registry_entry(
    language: TargetLanguage,
) -> None:
    """No silent dispatch hole when a new TargetLanguage enum value lands."""
    assert language in REGISTRY, (
        f"REGISTRY missing entry for {language}; this is the same class of "
        f"bug as Gap 1 from the 2026-04-27 e2e — adding a TargetLanguage "
        f"enum value without a registered LanguageAdapterEntry silently "
        f"breaks runs at LanguageAdapterSelector"
    )


@pytest.mark.parametrize("language", list(TargetLanguage))
def test_every_target_language_has_an_installer(
    language: TargetLanguage,
) -> None:
    """Same gating for the dependency-installer dispatch."""
    assert language in _INSTALLERS, (
        f"_INSTALLERS missing entry for {language}"
    )
