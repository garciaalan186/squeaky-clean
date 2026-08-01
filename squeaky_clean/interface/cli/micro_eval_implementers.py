"""micro_eval_implementers: per-language ImplementClass graphs (R5.4)."""

from __future__ import annotations

import os
from pathlib import Path

from squeaky_clean.application.generation.emission.implement_class import ImplementClass
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.llm.retrying_gateway import RetryingGateway
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector
from squeaky_clean.interface.cli.micro_eval_scaffold import LANGUAGES

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]


def build_implementers(
    router: ModelRouter, rc: RunConfig,
) -> dict[str, ImplementClass]:
    """One ImplementClass per micro-eval language.

    Mirrors DependencyBuilder's per-problem recipe: language-specific
    fence parser + Java's ICP-tier model promotion (Haiku misses Java
    contracts often enough that ICP routes to the manager model).
    """
    log = JSONLogger()
    gateway = _gateway(rc, log)
    fs = LocalFileSystem()
    loader = LoadAgentSpec()
    out: dict[str, ImplementClass] = {}
    for lang in LANGUAGES:
        toolkit = LanguageToolkitFactory().for_language(lang)
        adapters = LanguageAdapterSelector(log).select(toolkit, fs)
        out[lang.value] = ImplementClass(
            gateway, _icp_router(router, lang), rc,
            parser=ParseImplementedClass(adapters.parser), loader=loader,
        )
    return out


def _gateway(rc: RunConfig, log: RunLogger) -> LLMGateway:
    cache_dir = _FRAMEWORK_ROOT.parent / "meta-evaluation-results" / "cache"
    inner: LLMGateway = (
        AnthropicSDKGateway(logger=log) if os.environ.get("ANTHROPIC_API_KEY")
        else ClaudeCLIGateway(logger=log)
    )
    return CachingLLMGateway(RetryingGateway(inner, rc.retry_policy, logger=log), cache_dir)


# Languages whose ICP tier promotes to the manager model: Haiku misses their
# cross-file contracts (java 20/35 in R5.4; go 16/35 on the R6.1d inaugural
# sweep — sibling redeclaration, import hygiene, pointer-vs-value).
_PROMOTED_ICP_LANGUAGES: frozenset[TargetLanguage] = frozenset({
    TargetLanguage.JAVA, TargetLanguage.GO,
})


def _icp_router(base: ModelRouter, lang: TargetLanguage) -> ModelRouter:
    if lang not in _PROMOTED_ICP_LANGUAGES:
        return base
    mapping = {tier: base.route(tier) for tier in ModelTier}
    mapping[ModelTier.ICP] = mapping[ModelTier.MANAGER]
    return ModelRouter(mapping)
