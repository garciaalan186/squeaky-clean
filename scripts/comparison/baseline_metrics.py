"""BaselineComparisonMetrics: per-run metrics for the comparison harness.

Wraps the framework's existing EvalMetrics shape with comparison-specific
additions: line/branch coverage, retry count, parse-failure flag, and
prompt + translator version stamps for reproducibility.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BaselineComparisonMetrics:
    """Per-run metrics + reproducibility stamps for baseline comparisons."""

    # Identification
    framing: str                      # "1_practical" / "2_info_equivalent" / "3_equal_cost"
    system: str                       # "squeaky" / "vanilla-opus" / etc.
    replicate_id: int
    problem_id: str

    # Correctness
    tests_pass: float = 0.0
    compile_errors: int = 0
    architecture_violations: int = 0
    hallucinations: int = 0
    tests_runnable: bool = False
    parse_failure: bool = False
    parse_failure_reason: str = ""

    # Coverage
    coverage_line_pct: float = 0.0
    coverage_branch_pct: float = 0.0

    # Efficiency
    estimated_cost_usd: float = 0.0
    total_wall_clock_ms: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    retry_count: int = 0

    # Decomposition
    avg_file_line_count: float = 0.0
    max_file_line_count: int = 0
    classes_per_module: tuple[int, ...] = field(default_factory=tuple)
    orphan_files: int = 0

    # Reproducibility
    prompt_template_version: str = ""
    translator_version: str = ""
    framework_sha: str = ""
    model_id: str = ""

    def write(self, path: Path) -> None:
        """Serialize to JSON at `path`."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, sort_keys=True))

    @classmethod
    def read(cls, path: Path) -> "BaselineComparisonMetrics":
        """Load from a previously-written JSON file."""
        data = json.loads(path.read_text())
        if "classes_per_module" in data and isinstance(data["classes_per_module"], list):
            data["classes_per_module"] = tuple(data["classes_per_module"])
        return cls(**data)
