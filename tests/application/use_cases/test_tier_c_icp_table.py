"""Tests for tier_c_icp_table (category -> Tier C ICP routing table)."""

from squeaky_clean.application.generation.emission.routing.tier_c_icp_table import (
    CATEGORY_TO_ICP,
    INFRA_PATTERNS,
    INTERFACE_LAYER_CATEGORIES,
)


def test_every_icp_name_is_an_emitter() -> None:
    assert all(name.endswith("Emitter") for name in CATEGORY_TO_ICP.values())


def test_interface_layer_categories_are_a_subset_of_the_table() -> None:
    assert INTERFACE_LAYER_CATEGORIES <= set(CATEGORY_TO_ICP)


def test_interface_layer_categories_are_the_inbound_handlers() -> None:
    assert INTERFACE_LAYER_CATEGORIES == {
        "rest_server_handler", "grpc_server_handler",
        "websocket_server_handler",
    }


def test_infra_patterns_are_repository_gateway_adapter() -> None:
    assert INFRA_PATTERNS == {"Repository", "Gateway", "Adapter"}
