"""RefactorPlanSerializer: persist a RefactorPlan as refactor_plan.json."""

import json

from squeaky_clean.application.dtos.recovery.refactor_plan import RefactorPlan


class RefactorPlanSerializer:
    """Serializes a RefactorPlan to stable, diff-friendly JSON.

    The persisted plan records which violation ids the Refactor phase will
    address (`fix`) and which the reviewer chose to leave (`ignore`) — an
    auditable decision record that can be diffed and replayed.
    """

    def serialize(self, plan: RefactorPlan) -> str:
        """Return the refactor_plan.json text for a plan."""
        return json.dumps(
            {"fix": list(plan.fix), "ignore": list(plan.ignore)}, indent=2,
        )
