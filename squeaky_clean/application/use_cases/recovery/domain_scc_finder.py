"""DomainSCCFinder: strongly-connected components of the domain subgraph."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.domain.value_objects.layer_type import LayerType


class DomainSCCFinder:
    """Tarjan's SCC over the DOMAIN-layer induced subgraph of the catalog.

    Each returned component is a tuple of class FQNs that are mutually
    reachable through domain-to-domain imports; acyclic domains yield
    singleton components. Components (and their members) are sorted for
    deterministic output — the same catalog always yields the same list.
    """

    def components(
        self, catalog: ClassCatalog, layers: dict[str, LayerType],
    ) -> tuple[tuple[str, ...], ...]:
        """Return the domain subgraph's SCCs as sorted FQN tuples."""
        domain = {f for f, la in layers.items() if la is LayerType.DOMAIN}
        self._adj: dict[str, tuple[str, ...]] = {
            f: tuple(d for d in catalog.import_graph.get(f, ()) if d in domain)
            for f in sorted(domain)
        }
        self._index: dict[str, int] = {}
        self._low: dict[str, int] = {}
        self._stack: list[str] = []
        self._on: set[str] = set()
        self._out: list[tuple[str, ...]] = []
        self._n: int = 0
        for f in sorted(domain):
            if f not in self._index:
                self._connect(f)
        return tuple(self._out)

    def _connect(self, v: str) -> None:
        self._index[v] = self._low[v] = self._n
        self._n += 1
        self._stack.append(v)
        self._on.add(v)
        for w in self._adj[v]:
            if w not in self._index:
                self._connect(w)
                self._low[v] = min(self._low[v], self._low[w])
            elif w in self._on:
                self._low[v] = min(self._low[v], self._index[w])
        if self._low[v] == self._index[v]:
            self._out.append(self._pop_component(v))

    def _pop_component(self, root: str) -> tuple[str, ...]:
        comp: list[str] = []
        while True:
            w = self._stack.pop()
            self._on.discard(w)
            comp.append(w)
            if w == root:
                return tuple(sorted(comp))
