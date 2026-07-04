"""RefactorPlan DTO: the triage decision over analyzed violations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RefactorPlan:
    """Which violations the Refactor phase will address, and which to leave.

    `fix` and `ignore` hold violation ids (``category:target``). Triage
    defaults every violation to `fix` — the reviewer opts *out* by moving a
    category to `ignore`. Persisted as ``refactor_plan.json`` so the
    decision is auditable, diffable, and re-runnable against a later
    re-analysis of the same project.
    """

    fix: tuple[str, ...]
    ignore: tuple[str, ...]
