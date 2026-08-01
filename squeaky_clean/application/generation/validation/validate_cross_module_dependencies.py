"""validate_cross_module_dependencies: cross-module dep validator.

Thin application seam over the domain rule (R6.6c): the strict per-edge
checks live in ``domain/rules/cross_module_dependency_rules`` and are
surfaced by ``ArchitectureSpec.cross_module_dep_violations()``. This
function is kept so pipeline stages depend on a use-case-level callable
rather than on the entity method directly.
"""

from __future__ import annotations

from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


def validate_cross_module_dependencies(
    arch: ArchitectureSpec,
) -> tuple[str, ...]:
    """Return tuple of cross-module dependency violation strings."""
    return arch.cross_module_dep_violations()
