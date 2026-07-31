"""P0 Calculator: the smallest benchmark problem in the eval suite."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P0: ProblemSpec = ProblemSpec(
    id="P0",
    tier=0,
    slug="calculator",
    description="Calculator with four basic arithmetic operations",
    required_bounded_contexts=["calculator"],
    acceptance_criteria=[
        "Given operands 2 and 3, When add is called, Then result is 5",
        "Given operands 5 and 2, When subtract is called, Then result is 3",
        "Given operands 4 and 3, When multiply is called, Then result is 12",
        "Given operands 10 and 2, When divide is called, Then result is 5",
        "Given operands 1 and 0, When divide is called, Then an error is raised",
    ],
    expected_module_count=(1, 1),
    expected_class_count=(3, 6),
    required_patterns=["SimpleClass", "ValueObject"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 replicates, run 457 (2026-07-30), seeds 0-2.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.0,
        functional_pass_mean=1.0, functional_pass_stddev=0.0,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0187, cost_usd_stddev=0.0113,
        model_routing=(
            "architect=claude-sonnet-5",
            "fixer=claude-sonnet-5",
            "icp=claude-haiku-4-5-20251001",
            "manager=claude-sonnet-5",
        ),
        calibrated_run="meta-evaluation_457_20260730-164556",
    ),
)
