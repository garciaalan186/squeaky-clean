"""TestArchitectureSerializer: round-trip TestArchitecture to/from JSON (G3)."""

from __future__ import annotations

import json
from typing import Any

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton


class TestArchitectureSerializer:
    """Serialize/deserialize TestArchitecture (gherkin + skeletons) to JSON."""

    def serialize(self, arch: TestArchitecture) -> str:
        """Return JSON string capturing the gherkin scenarios + skeletons."""
        return json.dumps({
            "gherkin_scenarios": list(arch.gherkin_scenarios),
            "test_skeletons": [self._sk_to_dict(s) for s in arch.test_skeletons],
        }, indent=2)

    def deserialize(self, payload: str) -> TestArchitecture:
        """Parse JSON ``payload`` back into a TestArchitecture."""
        data: dict[str, Any] = json.loads(payload)
        return TestArchitecture(
            gherkin_scenarios=tuple(data["gherkin_scenarios"]),
            test_skeletons=tuple(
                self._sk_from_dict(d) for d in data["test_skeletons"]
            ),
        )

    def _sk_to_dict(self, sk: TestSkeleton) -> dict[str, Any]:
        return {
            "class_name": sk.class_name, "file_path": sk.file_path,
            "code": sk.code,
        }

    def _sk_from_dict(self, d: dict[str, Any]) -> TestSkeleton:
        return TestSkeleton(
            class_name=d["class_name"], file_path=d["file_path"], code=d["code"],
        )
