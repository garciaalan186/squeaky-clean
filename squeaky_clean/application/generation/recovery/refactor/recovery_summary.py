"""RecoverySummary DTO: the result of emitting a Squib + violations for review."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoverySummary:
    """What the front-half recovery run produced, for the CLI to report.

    `violations` is the total across all categories; `coupling_violations`
    is the framework-coupling subset that drives the MCDA verdict.
    `recommendation` is that verdict (``preserve`` or ``split``) under the
    user's criteria ranking; `recommendation_close` is true on a near-tie.
    `squib_path` and `violations_path` are where the faithful Squib and the
    categorized violations.json were written.
    """

    classes: int
    modules: int
    violations: int
    coupling_violations: int
    recommendation: str
    recommendation_close: bool
    squib_path: str
    violations_path: str
