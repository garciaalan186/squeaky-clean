"""Tests for the EmissionBundle DTO."""

import dataclasses

from squeaky_clean.interface.cli.wiring.emission_bundle import EmissionBundle


def test_bundle_is_frozen_with_the_three_emission_fields() -> None:
    fields = {f.name for f in dataclasses.fields(EmissionBundle)}
    assert fields == {"toolkit", "adapters", "orchestrate_module"}
    params = EmissionBundle.__dataclass_params__  # type: ignore[attr-defined]
    assert params.frozen is True
