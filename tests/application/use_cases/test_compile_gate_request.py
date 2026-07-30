"""Tests for CompileGateRequest (R2.4 extraction)."""

from pathlib import Path

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.compile_gate_request import CompileGateRequest


def test_construction_defaults() -> None:
    impl = ModuleImplementation(
        module=None, implemented_classes=(), total_cost_usd=0.0,  # type: ignore[arg-type]
        total_duration_ms=0, total_input_tokens=0, total_output_tokens=0,
        wall_duration_ms=0,
    )
    req = CompileGateRequest(impl, Path("/tmp"), max_passes=2)
    assert req.max_passes == 2 and req.architecture is None and req.toolkit is None
