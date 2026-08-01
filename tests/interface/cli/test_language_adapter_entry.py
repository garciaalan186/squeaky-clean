"""LanguageAdapterEntry is a frozen factory bundle."""

import dataclasses

import pytest

from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.interface.cli.language_adapters.language_adapter_entry import (
    LanguageAdapterEntry,
)
from squeaky_clean.interface.cli.language_adapters.scripted_language_entries import (
    scripted_entries,
)


def test_entry_is_frozen() -> None:
    entry = next(iter(scripted_entries().values()))
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.functional_exclude = "other"  # type: ignore[misc]


def test_compiler_defaults_to_none() -> None:
    fields = {f.name: f for f in dataclasses.fields(LanguageAdapterEntry)}
    assert fields["compiler"].default is None


def test_granularity_rule_field_is_a_zero_arg_factory() -> None:
    entry = scripted_entries()[next(iter(scripted_entries()))]
    assert isinstance(entry.granularity_rule(), PythonGranularityRule)
