"""validate_dependency_injection: flag orchestrators that inject no collaborator.

Deterministic post-architect check. An orchestrating class (UseCase, Facade)
does its work by delegating to a port; when the architect leaves its
`fields:` empty, the ICP still injects a port it infers, but the
TestArchitect — which predicts the constructor from `fields:` — cannot know
it, so generated tests instantiate the class with the wrong arity. Making
the injected collaborator explicit in `fields:` reconciles both agents.
"""

from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_ORCHESTRATORS: frozenset[str] = frozenset({"UseCase", "Facade"})
_COLLABORATORS: frozenset[str] = frozenset({"Gateway", "Repository"})


def validate_dependency_injection(arch: ArchitectureSpec) -> tuple[str, ...]:
    """Return one message per orchestrator with `fields: []` but a port to inject.

    Fires only when the class's own module provides a Gateway/Repository
    port — a strong signal the orchestrator must inject it — keeping the
    check free of false positives for genuinely stateless classes.
    """
    out: list[str] = []
    for module in arch.modules:
        ports = tuple(
            c.name for c in module.classes if c.pattern in _COLLABORATORS)
        if not ports:
            continue
        for c in module.classes:
            if c.pattern in _ORCHESTRATORS and c.methods and not c.fields:
                out.append(
                    f"{c.name} ({c.pattern}) declares fields: [] but its module "
                    f"provides port(s) {list(ports)} it must inject; declare the "
                    f"injected collaborator in fields: (e.g. "
                    f"fields: [{_camel(ports[0])}: {ports[0]}]).")
    return tuple(out)


def _camel(name: str) -> str:
    """PascalCase port name to a camelCase field name for the hint."""
    return name[:1].lower() + name[1:] if name else name
