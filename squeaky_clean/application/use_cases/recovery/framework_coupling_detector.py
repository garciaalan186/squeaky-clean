"""FrameworkCouplingDetector: flag domain classes welded to a foreign base."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.dtos.recovery.refactor_proposal import RefactorProposal
from squeaky_clean.domain.value_objects.layer_type import LayerType

_STDLIB_BASES: frozenset[str] = frozenset({
    "object", "ABC", "ABCMeta", "Enum", "IntEnum", "StrEnum", "Flag",
    "Exception", "BaseException", "Protocol", "NamedTuple", "TypedDict",
    "Generic", "dict", "list", "tuple", "set", "str", "int",
})


class FrameworkCouplingDetector:
    """Detects the Dependency-Rule violation ORM/Active-Record models embody.

    A DOMAIN-layer class inheriting a *foreign* base — one resolving to
    neither a sibling catalogued class nor the language standard library —
    is coupled to a framework and cannot be a clean Entity. The allowlist
    enumerates the stdlib (bounded, stable), never frameworks (unbounded),
    so this needs no per-framework knowledge. Each hit becomes a
    RefactorProposal recommending the Entity + Repository + Adapter split.
    """

    def detect_all(
        self, catalog: ClassCatalog, layers: dict[str, LayerType],
    ) -> tuple[RefactorProposal, ...]:
        """Return a proposal for every framework-coupled domain class."""
        siblings = {r.fqn.rsplit(".", 1)[-1] for r in catalog.classes}
        out: list[RefactorProposal] = []
        for record in catalog.classes:
            if layers.get(record.fqn) is not LayerType.DOMAIN:
                continue
            base = self._foreign_base(record, siblings)
            if base is not None:
                out.append(self._propose(record, base))
        return tuple(out)

    def _foreign_base(self, record: ClassRecord, siblings: set[str]) -> str | None:
        for base in record.bases:
            leaf = base.rsplit(".", 1)[-1].split("[", 1)[0].strip()
            if leaf and leaf not in _STDLIB_BASES and leaf not in siblings:
                return base
        return None

    def _propose(self, record: ClassRecord, base: str) -> RefactorProposal:
        name = record.fqn.rsplit(".", 1)[-1]
        return RefactorProposal(
            fqn=record.fqn, foreign_base=base, entity=name,
            repository=f"{name}Repository", adapter=f"{name}Adapter",
            reason=(
                f"domain class inherits framework base {base!r}; the "
                "Dependency Rule forbids business rules depending on a "
                "framework — extract a pure Entity behind a Repository port."
            ),
        )
