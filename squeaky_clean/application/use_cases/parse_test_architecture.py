"""ParseTestArchitecture: decode TestArchitect LLM output into a TestArchitecture."""

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.application.use_cases.test_architecture_gherkin_parser import (
    TestArchitectureGherkinParser,
)
from squeaky_clean.application.use_cases.test_architecture_skeletons_parser import (
    TestArchitectureSkeletonsParser,
)


class ParseTestArchitecture:
    """Parses the TestArchitect output format into a TestArchitecture DTO."""

    def __init__(self) -> None:
        self._gherkin: TestArchitectureGherkinParser = TestArchitectureGherkinParser()
        self._skeletons: TestArchitectureSkeletonsParser = (
            TestArchitectureSkeletonsParser()
        )

    def parse(self, raw: str) -> TestArchitecture:
        """Return a TestArchitecture built from TestArchitect raw output."""
        stripped = raw.strip()
        if "GHERKIN" not in stripped or "TEST_SKELETONS" not in stripped:
            raise TestArchitectureParseError(
                "missing GHERKIN or TEST_SKELETONS section header"
            )
        gherkin = self._gherkin.parse(stripped)
        skeletons = self._skeletons.parse(stripped)
        if not gherkin:
            raise TestArchitectureParseError("no Gherkin scenarios extracted")
        if not skeletons:
            raise TestArchitectureParseError("no test skeletons extracted")
        return TestArchitecture(
            gherkin_scenarios=gherkin,
            test_skeletons=skeletons,
        )
