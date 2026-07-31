"""P11 Notification Middleware: Decorator + Facade + Adapter + CoR (R5.6).

Architect-truncation flake RESOLVED 2026-07-30: root cause was sonnet's
adaptive thinking sharing the 4096 output-token default with the Squib
text (probe: 4466 tokens needed at end_turn). DesignArchitecture now
requests 16384; recalibration ran 3/3 with zero architect failures.
"""

from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P11: ProblemSpec = ProblemSpec(
    id="P11",
    tier=11,
    slug="notification_middleware",
    description=(
        "A notification middleware. Submitted messages pass through a chain "
        "of handlers: a validation handler rejects empty bodies, then a "
        "delivery handler sends the message. Message text can be wrapped in "
        "decorators: a prefix decorator prepends '[notice] ' and an uppercase "
        "decorator upper-cases the text. Delivery goes through an adapter "
        "over a legacy SMS client whose interface is send_text(number, "
        "body). A single facade exposes notify() over the whole stack."
    ),
    required_bounded_contexts=["notifications"],
    acceptance_criteria=[
        "Given a message with an empty body, When it is submitted to the handler chain, Then it is rejected by the validation handler and not delivered",
        "Given a message with body 'hi', When it is submitted to the handler chain, Then it reaches the delivery handler",
        "Given the text 'hi' wrapped in the prefix decorator, When rendered, Then the result is '[notice] hi'",
        "Given the text 'hi' wrapped in the uppercase decorator, When rendered, Then the result is 'HI'",
        "Given the text 'hi' wrapped in the uppercase decorator then the prefix decorator, When rendered, Then the result is '[notice] HI'",
        "Given the SMS adapter over the legacy client, When a message with body 'ping' is delivered to number '555', Then the legacy client's send_text receives number '555' and body 'ping'",
        "Given the notification facade, When notify is called with a valid message, Then a result with status 'sent' is returned",
        "Given the notification facade, When notify is called with an empty-body message, Then a result with status 'rejected' is returned",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(7, 20),
    required_patterns=[
        "ChainOfResponsibility", "Decorator", "Adapter", "Facade",
        "SimpleClass",
    ],
    target_language=TargetLanguage.PYTHON,
    # R5.6 golden: N=3, run 477 (2026-07-30), zero replicate failures.
    golden_metrics=GoldenMetrics(
        replicates=3,
        tests_pass_mean=0.7778, tests_pass_stddev=0.3849,
        functional_pass_mean=0.7778, functional_pass_stddev=0.3849,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.1326, cost_usd_stddev=0.0934,
        model_routing=(
            "architect=claude-sonnet-5",
            "fixer=claude-sonnet-5",
            "icp=claude-haiku-4-5-20251001",
            "manager=claude-sonnet-5",
        ),
        calibrated_run="meta-evaluation_477_20260730-220845",
    ),
)
