"""Hard gate: the product (generation/) must never import its eval harness.

The self-conformance ratchet grandfathers the remaining shared -> generation
edges, but generation -> evaluation is zero after R1.7 and must STAY zero — a
regression here means the product started depending on its own test harness.
This asserts it directly rather than trusting the baseline.
"""

from __future__ import annotations

from squeaky_clean.domain.rules.component_dependency_rule import ComponentDependencyRule
from tests.self_conformance.conformance_scan import package_root


def test_generation_never_imports_evaluation() -> None:
    offenders = [
        v for v in ComponentDependencyRule().check_tree(package_root())
        if v.message.startswith("generation/ imports evaluation/")
    ]
    assert not offenders, (
        "product must not import its eval harness:\n"
        + "\n".join(f"  {v.file_path}" for v in offenders)
    )
