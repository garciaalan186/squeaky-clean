"""TestArchitecture DTO: Gherkin scenarios + pytest skeletons from TestArchitect."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.test_skeleton import TestSkeleton


@dataclass(frozen=True)
class TestArchitecture:
    """Immutable bundle produced by the TestArchitect use case.

    `gherkin_scenarios` is one string per scenario in standard Gherkin
    form (``Feature:`` / ``Scenario:`` / ``Given`` / ``When`` / ``Then``
    lines joined by newlines). `test_skeletons` is one TestSkeleton per
    class declared by the source ModuleSpec.
    """

    gherkin_scenarios: tuple[str, ...]
    test_skeletons: tuple[TestSkeleton, ...]
