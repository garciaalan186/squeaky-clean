"""RefactorProposal DTO: a 1->N split for a framework-coupled domain class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RefactorProposal:
    """Recommends splitting a framework-coupled domain class per Clean Arch.

    A domain-layer class that inherits ``foreign_base`` (an external
    framework base, not a sibling or stdlib type) violates the Dependency
    Rule: business rules must not depend on a framework. The proposal
    replaces it with a pure ``entity`` (business rules, no framework), a
    ``repository`` port (the persistence boundary), and an ``adapter`` that
    implements the port using the framework — mapping rows to the entity.
    Advisory: the human applies it at the review gate.
    """

    fqn: str
    foreign_base: str
    entity: str
    repository: str
    adapter: str
    reason: str
