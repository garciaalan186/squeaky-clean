"""P9 Drawing Canvas: exercises Composite (shape tree) + Visitor (area traversal)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P9: ProblemSpec = ProblemSpec(
    id="P9",
    tier=9,
    slug="drawing_canvas",
    description=(
        "A drawing composed of shapes and groups. A rectangle has width and "
        "height; a group holds any number of shapes or nested groups, treated "
        "uniformly as a composite. An area visitor traverses the tree and "
        "computes the total area across all leaf shapes."
    ),
    required_bounded_contexts=["drawing"],
    acceptance_criteria=[
        "Given a group containing a rectangle 2 by 3 and a rectangle 4 by 5, When total area is computed, Then it is 26",
        "Given an empty group, When total area is computed, Then it is 0",
        "Given a group containing a rectangle 2 by 3, When another rectangle is added, Then the group child count is 2",
        "Given a group containing a nested group with a rectangle 3 by 3, When total area is computed, Then it is 9",
        "Given a single rectangle 5 by 4 visited by the area visitor, When its area is computed, Then it is 20",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 14),
    required_patterns=["Composite", "Visitor", "ValueObject", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0000, tests_pass_stddev=0.0000,
        functional_pass_mean=1.0000, functional_pass_stddev=0.0000,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0360, cost_usd_stddev=0.0050,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_503_20260730-233818",
    ),
)
