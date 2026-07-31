"""P1 Todo Manager: second-tier benchmark — in-memory CRUD + persistence."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P1: ProblemSpec = ProblemSpec(
    id="P1",
    tier=1,
    slug="todo_manager",
    description=(
        "In-memory todo manager that creates todos with titles, marks them "
        "complete, and lists pending ones. Titles must be non-empty."
    ),
    required_bounded_contexts=["todo"],
    acceptance_criteria=[
        "Given title 'Buy milk', When create_todo is called, Then the result title is 'Buy milk'",
        "Given title 'Task', When create_todo is called, Then the result is_pending is true",
        "Given a fresh todo with title 'Task', after mark_complete is called on it, Then is_pending returns false",
        "Given an empty title, When create_todo is called, Then a ValueError is raised",
        "Given a todo repository containing one pending todo and one completed todo, When list_pending is called, Then the result length is 1",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 12),
    required_patterns=["Entity", "ValueObject", "UseCase", "Repository"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3, meta-evaluation_482 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0000, tests_pass_stddev=0.0000,
        functional_pass_mean=1.0000, functional_pass_stddev=0.0000,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.1335, cost_usd_stddev=0.0195,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_482_20260730-225636",
    ),
)
