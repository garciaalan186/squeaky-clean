"""estimate_request_cost: a conservative pre-flight USD estimate for a request.

Used by BudgetedGateway to reserve budget BEFORE a call. Deliberately
over-estimates output (assumes the full ``max_tokens`` budget is used) so the
gate errs toward refusing a call rather than overspending.
"""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd

_CHARS_PER_TOKEN: int = 4
_DEFAULT_MAX_OUTPUT: int = 4096


def estimate_request_cost(
    request: LLMRequest, *, logger: RunLogger | None = None,
) -> float:
    """Return a conservative USD estimate for ``request``."""
    prompt_chars = len(request.system_prompt) + len(request.user_prompt)
    input_tokens = prompt_chars // _CHARS_PER_TOKEN
    output_tokens = request.max_tokens or _DEFAULT_MAX_OUTPUT
    return estimate_cost_usd(
        model=request.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_tokens=0,
        cache_read_tokens=0,
        logger=logger,
    )
