"""SweepRequest DTO: input to RunSweep.execute()."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.problem_spec import ProblemSpec


@dataclass(frozen=True)
class SweepRequest:
    """Bundle of problems + concurrency cap for one parallel sweep."""

    problems: tuple[ProblemSpec, ...]
    max_parallel: int = 4
