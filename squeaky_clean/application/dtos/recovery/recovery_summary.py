"""RecoverySummary DTO: the result of emitting a Squib for review."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoverySummary:
    """What the front-half recovery run produced, for the CLI to report.

    `recommendation` is the MCDA verdict for framework-coupled classes
    (``preserve`` or ``split``) under the user's criteria ranking;
    `recommendation_close` is true when that verdict was a near-tie and
    the human should weigh in. `squib_path` and `refactors_path` are where
    the reviewable Squib and the refactor sidecar were written.
    """

    classes: int
    modules: int
    proposals: int
    recommendation: str
    recommendation_close: bool
    squib_path: str
    refactors_path: str
