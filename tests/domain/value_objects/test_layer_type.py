"""Tests for LayerType."""

from squeaky_clean.domain.value_objects.layer_type import LayerType


def test_layer_type_has_four_members() -> None:
    assert set(LayerType) == {
        LayerType.DOMAIN,
        LayerType.APPLICATION,
        LayerType.INFRASTRUCTURE,
        LayerType.INTERFACE,
    }


def test_layer_type_values_are_strings() -> None:
    assert LayerType.DOMAIN.value == "domain"
