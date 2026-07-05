"""InteractiveTriage: opt-out, category-level review of violations."""

from collections.abc import Callable

from squeaky_clean.application.dtos.recovery.refactor_plan import RefactorPlan
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport


class InteractiveTriage:
    """Turns a ViolationReport into a RefactorPlan via category-level review.

    Every category is addressed by default; the injected ``ask`` callback
    is prompted once per category (``ask(category, count) -> bool``, True to
    fix) so the reviewer opts *out* of whole categories rather than wading
    through thousands of individual findings. Injecting ``ask`` keeps the
    triage logic pure and testable; the CLI supplies a console prompt.
    """

    def run(
        self, report: ViolationReport, ask: Callable[[str, int], bool],
    ) -> RefactorPlan:
        """Return the RefactorPlan from per-category fix/ignore decisions."""
        grouped = report.by_category()
        fix: list[str] = []
        ignore: list[str] = []
        for category in sorted(grouped):
            items = grouped[category]
            bucket = fix if ask(category, len(items)) else ignore
            bucket.extend(v.violation_id for v in items)
        return RefactorPlan(fix=tuple(fix), ignore=tuple(ignore))
