"""P11 Notification Middleware: Decorator + Facade + Adapter + CoR (R5.6).

KNOWN FLAKE (2026-07-30): the architect's Squib emission for this brief
truncates mid-structure ("unbalanced {}") in ~3/5 live attempts (~450
output tokens, far below max_tokens — early stop, not a cap). When the
emission parses, the problem passes 1.00 end-to-end (run 471). No golden
until the truncation is root-caused (candidates: prompt-cache block
boundaries R3.5, retry-prompt determinism). Replicate calibration also
needs per-replicate error isolation (dies on first failed replicate).
"""

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
)
