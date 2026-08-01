"""Tests for the TierSampling value object."""

import pytest

from squeaky_clean.domain.value_objects.sampling.tier_sampling import TierSampling


def test_holds_temperature_and_seed() -> None:
    s = TierSampling(temperature=0.2, seed=0)
    assert s.temperature == 0.2
    assert s.seed == 0


def test_seed_may_be_none() -> None:
    assert TierSampling(temperature=0.0, seed=None).seed is None


def test_is_frozen() -> None:
    s = TierSampling(temperature=0.0, seed=0)
    with pytest.raises(AttributeError):
        s.temperature = 1.0  # type: ignore[misc]
