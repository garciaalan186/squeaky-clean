"""DependencyBuilder: constructs RunEvalDependencies for the CLI."""
import os
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.budgeted_gateway import BudgetedGateway
from squeaky_clean.application.use_cases.cost_gate import CostGate
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.use_cases.fix_failing_classes_deps import FixFailingClassesDeps
from squeaky_clean.application.use_cases.generate_security_tests import GenerateSecurityTests
from squeaky_clean.application.use_cases.generate_test_architecture import GenerateTestArchitecture
from squeaky_clean.application.use_cases.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.infrastructure_choice_architect import (
    InfrastructureChoiceArchitect,
)
from squeaky_clean.application.use_cases.integrate_module import IntegrateModule
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.mcda_registry import MCDARegistry
from squeaky_clean.application.use_cases.mcda_scorer import MCDAScorer
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.application.use_cases.parse_implemented_class import ParseImplementedClass
from squeaky_clean.application.use_cases.review_security import ReviewSecurity
from squeaky_clean.application.use_cases.rule_runner import RuleRunner
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.use_cases.techspec_composer import TechSpecComposer
from squeaky_clean.application.use_cases.validate_architecture import ValidateArchitecture
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.domain.rules.dependency_rule import DependencyRule
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.metrics.eval_metric_collector import EvalMetricCollector
from squeaky_clean.infrastructure.sast.bandit_sast_runner import BanditSastRunner
from squeaky_clean.infrastructure.techspec.allowlist_loader import (
    load_allowlist_registry,
)
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver import (
    CompositeTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.filesystem_techspec_resolver import (
    FilesystemTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)
from squeaky_clean.infrastructure.techspec.mcp_tech_doc_fetcher import MCPTechDocFetcher
from squeaky_clean.infrastructure.techspec.webfetch_tech_doc_fetcher import (
    WebFetchTechDocFetcher,
)
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector


class DependencyBuilder:
    """Builds a fully-wired RunEvalDependencies from a router + problem."""

    def build(
        self, router: ModelRouter, problem: ProblemSpec,
        run_config: RunConfig | None = None,
    ) -> RunEvalDependencies:
        """Return a RunEvalDependencies with every collaborator instantiated."""
        rc = run_config or RunConfig()
        # Cache dir lives next to meta-evaluation-results, anchored relative
        # to the framework checkout so this runs from any clone.
        framework_root = Path(__file__).resolve().parents[3]
        cache_dir = framework_root.parent / "meta-evaluation-results" / "cache"
        cost_gate = CostGate(rc.cost_budget)
        gateway: LLMGateway = BudgetedGateway(
            CachingLLMGateway(self._select_inner_gateway(rc), cache_dir),
            cost_gate,
        )
        fs = LocalFileSystem()
        toolkit = LanguageToolkitFactory().for_language(problem.target_language)
        adapters = LanguageAdapterSelector().select(toolkit, fs)
        assigner = AssignPatterns(
            toolkit, Path(""),
            infrastructure_mode=rc.infrastructure_mode,
        )
        icp_router = self._icp_router(router, problem.target_language)
        composer = (
            TechSpecComposer(gateway) if rc.infrastructure_mode == "auto" else None
        )
        parser = ParseImplementedClass(adapters.parser)
        orchestrator = OrchestrateModule(
            ImplementClass(
                gateway, icp_router, rc, composer=composer, parser=parser,
            ),
            assigner,
        )
        recorder = LLMUsageRecorder()
        call_deps = LLMCallDeps(
            gateway=gateway, router=router, recorder=recorder, run_config=rc,
        )
        ta_deps = GenerateTestArchitectureDeps(
            gateway=gateway, router=router, toolkit=toolkit, recorder=recorder,
            run_config=rc,
        )
        rules: tuple[Rule, ...] = (adapters.granularity_rule,)
        if problem.target_language is TargetLanguage.PYTHON:
            rules = (adapters.granularity_rule, DependencyRule())
        rule_runner = RuleRunner(rules, toolkit.file_extension)
        fixer = FixFailingClasses(FixFailingClassesDeps(
            gateway=gateway, router=router, recorder=recorder, toolkit=toolkit,
            run_config=rc,
        ))
        return RunEvalDependencies(
            design_architecture=DesignArchitecture(call_deps),
            generate_test_architecture=GenerateTestArchitecture(ta_deps),
            orchestrate_module=orchestrator,
            integrate_module=IntegrateModule(fs, adapters.bootstrap),
            validate_architecture=ValidateArchitecture(
                rule_runner, toolkit.file_extension
            ),
            test_runner=adapters.test_runner,
            metric_collector=EvalMetricCollector(),
            functional_test_runner=adapters.functional_test_runner,
            llm_usage_recorder=recorder,
            review_security=ReviewSecurity(call_deps),
            generate_security_tests=GenerateSecurityTests(ta_deps),
            fix_failing_classes=fixer,
            file_system=fs,
            run_config=rc,
            cost_gate=cost_gate,
            sast_runner=BanditSastRunner() if rc.enable_sast else None,
            model_router=router,
            tech_spec_resolver=self._tech_spec_resolver(rc),
            infrastructure_choice_architect=self._infra_choice_architect(rc, gateway),
            dependency_installer=adapters.dependency_installer,
        )

    @staticmethod
    def _infra_choice_architect(
        rc: RunConfig, gateway: LLMGateway,
    ) -> InfrastructureChoiceArchitect | None:
        if rc.infrastructure_mode != "auto" or not rc.infer_infrastructure:
            return None
        scores_root = (
            Path(__file__).resolve().parents[3] / "eval" / "mcda_scores"
        )
        if not scores_root.is_dir():
            return None
        return InfrastructureChoiceArchitect(
            gateway, MCDARegistry(scores_root), MCDAScorer(),
        )

    @staticmethod
    def _tech_spec_resolver(
        rc: RunConfig,
    ) -> TechSpecResolver | None:
        if rc.infrastructure_mode != "auto":
            return None
        eval_root = (
            Path(__file__).resolve().parents[3] / "eval" / "tech_specs"
        )
        schema_path = eval_root / "_schema.v1.json"
        if not schema_path.is_file():
            return None
        validator = JSONSchemaTechSpecValidator(schema_path)
        fs_resolver = FilesystemTechSpecResolver(eval_root, validator)
        return CompositeTechSpecResolver(
            fs_resolver, validator,
            cache_root=eval_root / ".cache",
            ttl_days=rc.techspec_cache_ttl_days,
            mcp_fetcher=MCPTechDocFetcher(),
            web_fetcher=WebFetchTechDocFetcher(),
            allowlist_registry=load_allowlist_registry(eval_root),
        )

    @staticmethod
    def _icp_router(base: ModelRouter, lang: TargetLanguage) -> ModelRouter:
        if lang is not TargetLanguage.JAVA:
            return base
        m = {t: base.route(t) for t in ModelTier}
        m[ModelTier.ICP] = m[ModelTier.MANAGER]
        return ModelRouter(m)

    @staticmethod
    def _select_inner_gateway(rc: RunConfig) -> LLMGateway:
        """Use SDK gateway iff ANTHROPIC_API_KEY is in env, else CLI."""
        if os.environ.get("ANTHROPIC_API_KEY"):
            return AnthropicSDKGateway(
                prompt_cache_config=rc.prompt_cache_config,
            )
        return ClaudeCLIGateway()
