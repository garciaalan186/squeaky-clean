"""RefactorProposalRenderer: render refactor proposals as a review sidecar."""

from squeaky_clean.application.dtos.recovery.refactor_proposal import RefactorProposal


class RefactorProposalRenderer:
    """Renders RefactorProposals into a human-readable markdown note.

    Emitted alongside the recovered Squib so the reviewer sees which
    framework-coupled classes should be split before regeneration. When
    there are no proposals the note says so explicitly rather than being
    absent, so a clean result is distinguishable from a skipped step.
    """

    def render(self, proposals: tuple[RefactorProposal, ...]) -> str:
        """Return a markdown document describing the proposed refactors."""
        if not proposals:
            return "# Refactor proposals\n\nNone — no framework-coupled "\
                   "domain classes detected.\n"
        header = (
            f"# Refactor proposals\n\n{len(proposals)} domain class(es) are "
            "coupled to a framework base and should be split before "
            "regeneration (Clean Architecture: the database is a detail).\n\n"
        )
        return header + "".join(self._entry(p) for p in proposals)

    def _entry(self, proposal: RefactorProposal) -> str:
        return (
            f"- `{proposal.fqn}` (base `{proposal.foreign_base}`)\n"
            f"  → `{proposal.entity}` (Entity) + `{proposal.repository}` "
            f"(Repository port) + `{proposal.adapter}` (framework Adapter).\n"
            f"  {proposal.reason}\n"
        )
