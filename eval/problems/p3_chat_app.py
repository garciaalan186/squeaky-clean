"""P3 Chat Application: highest-tier benchmark — multi-entity, authorization, events."""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P3: ProblemSpec = ProblemSpec(
    id="P3",
    tier=3,
    slug="chat_app",
    description=(
        "In-memory chat application where users join rooms, send messages, "
        "and retrieve history. Only room members may send. Message content "
        "must be non-empty. Rooms track their members and message history."
    ),
    required_bounded_contexts=["chat"],
    acceptance_criteria=[
        "Given username 'Alice', When create_user is called, Then the user name is 'Alice'",
        "Given room name 'General', When create_room is called, Then the room name is 'General'",
        "Given user 'Alice' and room 'General', When join_room is called, Then the room member_count is 1",
        "Given 'Alice' is a member of 'General', When send_message is called with content 'Hello', Then the room message_count is 1",
        "Given 'Alice' sent 'Hello' in 'General', When get_history is called, Then the result length is 1",
        "Given 'Bob' is not a member of 'General', When send_message is called, Then a ValueError is raised",
        "Given 'Alice' is a member of 'General', When send_message is called with empty content, Then a ValueError is raised",
    ],
    expected_module_count=(1, 4),
    expected_class_count=(6, 15),
    required_patterns=["Entity", "ValueObject", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
    # R5.2 golden: N=3, meta-evaluation_485 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.7333, tests_pass_stddev=0.3055,
        functional_pass_mean=0.7333, functional_pass_stddev=0.3055,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.0921, cost_usd_stddev=0.0230,
        model_routing=(
        "architect=claude-sonnet-5",
        "fixer=claude-sonnet-5",
        "icp=claude-haiku-4-5-20251001",
        "manager=claude-sonnet-5",
    ),
        calibrated_run="meta-evaluation_485_20260730-230028",
    ),
)
