"""TestArchitectureGherkinParser: extract Gherkin scenarios from TestArchitect output."""

import re

_GHERKIN_SECTION = re.compile(
    r"GHERKIN\s*\n-{3,}\s*\n(?P<body>.*?)\n-{3,}\s*(?:\n|$)",
    re.DOTALL,
)


class TestArchitectureGherkinParser:
    """Extracts one string per `Scenario:` block from the GHERKIN section."""

    def parse(self, raw: str) -> tuple[str, ...]:
        """Return a tuple of scenario strings extracted from raw output."""
        match = _GHERKIN_SECTION.search(raw)
        if match is None:
            return ()
        body = match.group("body").strip()
        if not body:
            return ()
        return self._split_scenarios(body)

    def _split_scenarios(self, body: str) -> tuple[str, ...]:
        lines = body.splitlines()
        feature_line = ""
        scenarios: list[list[str]] = []
        current: list[str] | None = None
        for raw_line in lines:
            line = raw_line.rstrip()
            stripped = line.strip()
            if stripped.startswith("Feature:"):
                feature_line = stripped
                continue
            if stripped.startswith("Scenario:"):
                if current is not None:
                    scenarios.append(current)
                current = [feature_line, stripped] if feature_line else [stripped]
                continue
            if current is not None and stripped:
                current.append(stripped)
        if current is not None:
            scenarios.append(current)
        return tuple("\n".join(s) for s in scenarios)
