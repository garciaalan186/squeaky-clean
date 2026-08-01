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
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.llm.retrying_gateway import RetryingGateway
from squeaky_clean.interface.cli.language_adapter_selector import (
    LanguageAdapterSelector,
)

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
_LANGUAGES: tuple[TargetLanguage, ...] = (
    TargetLanguage.PYTHON, TargetLanguage.JAVA, TargetLanguage.TYPESCRIPT,
)


def build_implementers(
    router: ModelRouter, rc: RunConfig,
) -> dict[str, ImplementClass]:
    """One ImplementClass per micro-eval language.

    Mirrors DependencyBuilder's per-problem recipe: language-specific
    fence parser + Java's ICP-tier model promotion (Haiku misses Java
    contracts often enough that ICP routes to the manager model).
    """
    gateway = _gateway(rc)
    fs = LocalFileSystem()
    loader = LoadAgentSpec()
    out: dict[str, ImplementClass] = {}
    for lang in _LANGUAGES:
        toolkit = LanguageToolkitFactory().for_language(lang)
        adapters = LanguageAdapterSelector().select(toolkit, fs)
        out[lang.value] = ImplementClass(
            gateway, _icp_router(router, lang), rc,
            parser=ParseImplementedClass(adapters.parser), loader=loader,
        )
    return out


def _gateway(rc: RunConfig) -> LLMGateway:
    cache_dir = _FRAMEWORK_ROOT.parent / "meta-evaluation-results" / "cache"
    inner: LLMGateway = (
        AnthropicSDKGateway() if os.environ.get("ANTHROPIC_API_KEY")
        else ClaudeCLIGateway()
    )
    return CachingLLMGateway(RetryingGateway(inner, rc.retry_policy), cache_dir)


def _icp_router(base: ModelRouter, lang: TargetLanguage) -> ModelRouter:
    if lang is not TargetLanguage.JAVA:
        return base
    mapping = {tier: base.route(tier) for tier in ModelTier}
    mapping[ModelTier.ICP] = mapping[ModelTier.MANAGER]
    return ModelRouter(mapping)
