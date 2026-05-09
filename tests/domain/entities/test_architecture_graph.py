"""Unit tests for ArchitectureGraph cycle detection."""

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph


def test_empty_graph_is_dag() -> None:
    g = ArchitectureGraph(edges={})
    assert g.is_dag() is True
    assert g.cycle_violations() == ()


def test_linear_chain_is_dag() -> None:
    g = ArchitectureGraph(edges={"a": ("b",), "b": ("c",), "c": ()})
    assert g.is_dag() is True


def test_self_loop_detected() -> None:
    g = ArchitectureGraph(edges={"a": ("a",)})
    assert g.is_dag() is False
    cycles = g.cycle_violations()
    assert any("a -> a" in c for c in cycles)


def test_two_node_cycle_detected() -> None:
    g = ArchitectureGraph(edges={"a": ("b",), "b": ("a",)})
    assert g.is_dag() is False


def test_three_node_cycle_detected() -> None:
    g = ArchitectureGraph(edges={"a": ("b",), "b": ("c",), "c": ("a",)})
    assert g.is_dag() is False


def test_diamond_no_cycle() -> None:
    g = ArchitectureGraph(edges={
        "a": ("b", "c"), "b": ("d",), "c": ("d",), "d": ()
    })
    assert g.is_dag() is True
