"""Tests for MCDARegistryEntryMissingError."""

import pytest

from squeaky_clean.application.shared.mcda.mcda_registry_entry_missing_error import (
    MCDARegistryEntryMissingError,
)


def test_is_a_key_error() -> None:
    assert issubclass(MCDARegistryEntryMissingError, KeyError)


def test_carries_category_message() -> None:
    with pytest.raises(MCDARegistryEntryMissingError, match="ghost"):
        raise MCDARegistryEntryMissingError("no MCDA registry file for 'ghost'")
