"""Tests for micro_eval_implementers (R5.4) — offline construction only."""

from squeaky_clean.application.generation.emission.implement_class import (
    ImplementClass,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.interface.cli.micro_eval_implementers import build_implementers
from squeaky_clean.interface.cli.router_factory import RouterFactory


def test_builds_one_implementer_per_language() -> None:
    implementers = build_implementers(
        RouterFactory().build(None), RunConfig(),
    )
    assert set(implementers) == {"python", "java", "typescript"}
    assert all(isinstance(i, ImplementClass) for i in implementers.values())
