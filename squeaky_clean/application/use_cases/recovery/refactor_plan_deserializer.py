"""RefactorPlanDeserializer: load a persisted refactor_plan.json."""

import json

from squeaky_clean.application.dtos.recovery.refactor_plan import RefactorPlan


class RefactorPlanDeserializer:
    """Rebuilds a RefactorPlan from its persisted JSON.

    The inverse of RefactorPlanSerializer, so the Refactor phase can run
    against a triage decision made in an earlier step — each phase is
    independently re-runnable from its persisted output.
    """

    def deserialize(self, text: str) -> RefactorPlan:
        """Return the RefactorPlan encoded in ``text``."""
        data = json.loads(text)
        return RefactorPlan(
            fix=tuple(data["fix"]), ignore=tuple(data["ignore"]),
        )
