"""validate_contract_fidelity: cross-service contract validator (pure function)."""

from __future__ import annotations

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec


def validate_contract_fidelity(
    arch: ArchitectureSpec,
    problem: ProblemSpec,
    registry: ContractRegistry,
) -> tuple[str, ...]:
    """Return violation strings for produces/consumes mismatches; empty if OK."""
    out: list[str] = []
    entities = _entity_classes(arch)
    for ref in problem.consumes_contracts:
        contract = registry.lookup(ref.contract_name)
        if contract is None:
            out.append(
                f"consumed contract {ref.contract_name!r} not registered; "
                "producer service must emit it first")
            continue
        out.extend(_check_consumed(contract, entities))
    for produced in problem.produces_contracts:
        out.extend(_check_produced(produced, entities))
    return tuple(out)


def _entity_classes(arch: ArchitectureSpec) -> tuple[ClassSpec, ...]:
    return tuple(
        c for m in arch.modules for c in m.classes
        if c.pattern == "Entity")


def _normalize(name: str) -> str:
    """Collapse to lowercase + strip underscores so snake_case and camelCase
    match: ``received_at`` and ``receivedAt`` both → ``receivedat``. Lets
    cross-language naming differences (Python snake_case vs Java camelCase)
    pass contract validation while still catching real semantic mismatches.
    """
    return name.lower().replace("_", "")


def _field_names(cls: ClassSpec) -> frozenset[str]:
    out: set[str] = set()
    for entry in cls.fields:
        head, _, _ = entry.partition(":")
        head = head.strip()
        if head:
            out.add(_normalize(head))
    return frozenset(out)


def _check_consumed(
    contract: Contract, entities: tuple[ClassSpec, ...],
) -> tuple[str, ...]:
    needed = frozenset(_normalize(n) for n in contract.required_field_names())
    for cls in entities:
        if needed.issubset(_field_names(cls)):
            return ()
    return (
        f"consumed contract {contract.name!r} requires fields "
        f"{sorted(needed)} but no Entity class declares all of them",)


def _check_produced(
    contract: Contract, entities: tuple[ClassSpec, ...],
) -> tuple[str, ...]:
    needed = frozenset(_normalize(n) for n in contract.all_field_names())
    for cls in entities:
        if needed.issubset(_field_names(cls)):
            return ()
    return (
        f"produced contract {contract.name!r} declares fields "
        f"{sorted(needed)} but no Entity class declares all of them",)
