"""ContractSectionRenderer: emit ProducesContracts / ConsumesContracts blocks."""

from __future__ import annotations

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry


class ContractSectionRenderer:
    """Renders cross-service contract sections of the architect prompt."""

    def __init__(self, registry: ContractRegistry) -> None:
        self._registry: ContractRegistry = registry

    def render(self, lines: list[str], problem: ProblemSpec) -> None:
        """Append ProducesContracts / ConsumesContracts sections in place."""
        if problem.produces_contracts:
            lines.append("ProducesContracts:")
            for c in problem.produces_contracts:
                fields = ", ".join(f"{f.name}: {f.type}" for f in c.fields)
                lines.append(f"  - {c.name} via {c.transport} -> [{fields}]")
        if problem.consumes_contracts:
            lines.append("ConsumesContracts:")
            for ref in problem.consumes_contracts:
                resolved = self._registry.lookup(ref.contract_name)
                if resolved is None:
                    lines.append(f"  - {ref.contract_name}: NOT_REGISTERED")
                    continue
                fields = ", ".join(
                    f"{f.name}: {f.type}" for f in resolved.fields)
                lines.append(
                    f"  - {resolved.name} via {resolved.transport} -> "
                    f"[{fields}]")
