"""GatewayStackFactory: builds the budgeted/caching/retrying LLM gateway stack."""

import os
from pathlib import Path

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.budgeted_gateway import BudgetedGateway
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.cache_miss_raiser import CacheMissRaiser
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.cost_estimator import estimate_request_cost
from squeaky_clean.infrastructure.llm.retrying_gateway import RetryingGateway


class GatewayStackFactory:
    """Wires cost gate + caching + retry around the configured inner gateway."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._log: RunLogger = logger or NullRunLogger()

    def build(self, run_config: RunConfig) -> tuple[LLMGateway, CostGate]:
        """Return the fully-decorated gateway and its cost gate."""
        cost_gate = CostGate(run_config.cost_budget)
        gateway: LLMGateway = BudgetedGateway(
            CachingLLMGateway(
                RetryingGateway(
                    (CacheMissRaiser() if run_config.replay_only
                     else self._select_inner_gateway(run_config)),
                    run_config.retry_policy,
                    logger=self._log,
                ),
                self._cache_dir(),
            ),
            cost_gate,
            estimator=self._estimator,
        )
        return gateway, cost_gate

    def _estimator(self, request: LLMRequest) -> float:
        """Pre-flight estimate with this run's logger threaded through."""
        return estimate_request_cost(request, logger=self._log)

    @staticmethod
    def _cache_dir() -> Path:
        # Cache dir lives next to meta-evaluation-results, anchored relative
        # to the framework checkout so this runs from any clone.
        framework_root = Path(__file__).resolve().parents[4]
        # R5.7: SQUEAKY_CACHE_DIR lets CI point at a committed replay bundle.
        return Path(os.environ.get(
            "SQUEAKY_CACHE_DIR",
            framework_root.parent / "meta-evaluation-results" / "cache",
        ))

    def _select_inner_gateway(self, rc: RunConfig) -> LLMGateway:
        """Use SDK gateway iff ANTHROPIC_API_KEY is in env, else CLI."""
        if os.environ.get("ANTHROPIC_API_KEY"):
            return AnthropicSDKGateway(
                prompt_cache_config=rc.prompt_cache_config,
                logger=self._log,
            )
        return ClaudeCLIGateway(logger=self._log)
