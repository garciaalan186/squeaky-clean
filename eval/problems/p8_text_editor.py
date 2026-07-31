"""P8 Text Editor: exercises Command (operations) + Memento (undo snapshot)."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P8: ProblemSpec = ProblemSpec(
    id="P8",
    tier=8,
    slug="text_editor",
    description=(
        "A text buffer supporting insert and delete operations modelled as "
        "commands. Before each command executes it captures the buffer state as "
        "a memento, so a single-level undo restores the previous content. Insert "
        "appends text; delete removes a given number of trailing characters."
    ),
    required_bounded_contexts=["editing"],
    acceptance_criteria=[
        "Given an empty buffer, When an insert command for 'hello' is executed, Then the buffer content is 'hello'",
        "Given a buffer 'hello', When a delete command for 2 characters is executed, Then content is 'hel'",
        "Given a buffer 'hello' after an insert command, When undo is called, Then content is restored to the value before the insert",
        "Given a buffer with no executed command, When undo is called, Then content is unchanged",
        "Given a buffer 'ab', When an insert command for 'c' is executed and then undone, Then content is 'ab'",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 14),
    required_patterns=["Entity", "Command", "Memento", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.8333, tests_pass_stddev=0.2887,
        functional_pass_mean=0.8333, functional_pass_stddev=0.2887,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0715, cost_usd_stddev=0.0165,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_500_20260730-233535",
    ),
)
