"""P7 Order Lifecycle: exercises the State pattern (state-dependent transitions)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P7: ProblemSpec = ProblemSpec(
    id="P7",
    tier=7,
    slug="order_lifecycle",
    description=(
        "An order whose status moves through a lifecycle: Pending -> Paid -> "
        "Shipped -> Delivered. Each state permits only its one valid forward "
        "transition (pay, ship, deliver respectively); any other transition "
        "raises an error. Delivered is terminal. Behaviour is state-dependent, "
        "with each status implemented as a distinct state."
    ),
    required_bounded_contexts=["ordering"],
    acceptance_criteria=[
        "Given a new order, Then its status is 'Pending'",
        "Given a pending order, When pay is called, Then status is 'Paid'",
        "Given a paid order, When ship is called, Then status is 'Shipped'",
        "Given a shipped order, When deliver is called, Then status is 'Delivered'",
        "Given a pending order, When ship is called, Then a ValueError is raised",
        "Given a delivered order, When pay is called, Then a ValueError is raised",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 12),
    required_patterns=["Entity", "ValueObject", "State", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.3333, tests_pass_stddev=0.1650,
        functional_pass_mean=0.3333, functional_pass_stddev=0.1650,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.1056, cost_usd_stddev=0.0062,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_497_20260730-233117",
    ),
)
