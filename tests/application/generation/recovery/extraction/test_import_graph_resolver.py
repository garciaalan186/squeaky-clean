"""Tests for ImportGraphResolver: raw imports -> intra-project class edges."""

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.extraction.import_graph_resolver import (
    ImportGraphResolver,
)


def _record(fqn: str, imports: tuple[str, ...]) -> ClassRecord:
    return ClassRecord(
        fqn=fqn, bases=(), methods=(), fields=(), imports=imports, decorators=(),
    )


def test_only_catalogued_targets_become_edges() -> None:
    records = (
        _record("p.a.A", ("p.b.B", "os.path", "requests.Session")),
        _record("p.b.B", ()),
    )
    graph = ImportGraphResolver().resolve(records)
    assert graph == {"p.a.A": ("p.b.B",), "p.b.B": ()}


def test_self_edges_are_excluded_and_duplicates_dropped() -> None:
    records = (
        _record("p.a.A", ("p.a.A", "p.b.B", "p.b.B")),
        _record("p.b.B", ()),
    )
    graph = ImportGraphResolver().resolve(records)
    assert graph["p.a.A"] == ("p.b.B",)


def test_every_record_gets_a_key_even_with_no_edges() -> None:
    records = (_record("p.a.A", ()), _record("p.b.B", ()))
    graph = ImportGraphResolver().resolve(records)
    assert set(graph) == {"p.a.A", "p.b.B"}


def test_edge_order_follows_import_order() -> None:
    records = (
        _record("p.a.A", ("p.c.C", "p.b.B")),
        _record("p.b.B", ()),
        _record("p.c.C", ()),
    )
    assert ImportGraphResolver().resolve(records)["p.a.A"] == ("p.c.C", "p.b.B")
