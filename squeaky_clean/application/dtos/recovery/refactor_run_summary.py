"""RefactorRunSummary DTO: the result of applying a RefactorPlan to a Squib."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RefactorRunSummary:
    """What the Refactor phase produced, for the CLI to report.

    `classes_before` / `classes_after` bracket the 1->N growth from the
    applied splits; `modules` is the refactored module count (including the
    new ``<Module>Infra`` adapter modules). `out_path` is where the
    refactored Squib was written, ready for regeneration.
    """

    classes_before: int
    classes_after: int
    modules: int
    out_path: str
