"""ImportGraphResolver: resolve raw imports to intra-project class edges."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord


class ImportGraphResolver:
    """Builds a class-FQN dependency graph from ClassRecord imports.

    Each record's raw import targets are filtered to those that exactly
    match another catalogued class FQN; stdlib and third-party imports
    fall away because they are absent from the catalog. The result maps
    every class FQN to the ordered, de-duplicated FQNs it imports, with
    self-edges excluded. Deterministic — no LLM, no I/O.
    """

    def resolve(
        self, records: tuple[ClassRecord, ...],
    ) -> dict[str, tuple[str, ...]]:
        """Return an FQN -> imported-sibling-FQNs graph over the catalog."""
        known = {r.fqn for r in records}
        graph: dict[str, tuple[str, ...]] = {}
        for record in records:
            edges: list[str] = []
            for target in record.imports:
                if target in known and target != record.fqn and target not in edges:
                    edges.append(target)
            graph[record.fqn] = tuple(edges)
        return graph
