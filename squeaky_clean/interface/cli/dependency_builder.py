"""DependencyBuilder: constructs RunEvalDependencies for the CLI."""
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.run_manifest import RunManifest
from squeaky_clean.application.generation.architecture.design_architecture import DesignArchitecture
from squeaky_clean.application.generation.integration.integrate_module import IntegrateModule
from squeaky_clean.application.generation.repair.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.generation.repair.fix_failing_classes_deps import (
    FixFailingClassesDeps,
)
from squeaky_clean.application.generation.repair.repair_test_file import RepairTestFile
from squeaky_clean.application.generation.security.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.generation.security.review_security import ReviewSecurity
from squeaky_clean.application.generation.testgen.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.generation.testgen.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.generation.validation.validate_architecture import (
    ValidateArchitecture,
)
from squeaky_clean.application.generation.validation.verify_layer import VerifyLayer
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.metrics.eval_metric_collector import EvalMetricCollector
from squeaky_clean.infrastructure.observability.git_info_adapter import GitInfoAdapter
from squeaky_clean.infrastructure.observability.toolchain_probe_adapter import (
    ToolchainProbeAdapter,
)
from squeaky_clean.infrastructure.sast.bandit_sast_runner import BanditSastRunner
from squeaky_clean.interface.cli.language_compiler_factory import (
    LanguageCompilerFactory,
)
from squeaky_clean.interface.cli.wiring.emission_wiring import EmissionWiring
from squeaky_clean.interface.cli.wiring.rule_runner_factory import RuleRunnerFactory
from squeaky_clean.interface.cli.wiring.techspec_wiring import TechSpecWiring
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


class DependencyBuilder:
    """Builds a fully-wired RunEvalDependencies for one problem run."""

    def __init__(
        self, router: ModelRouter, run_config: RunConfig | None = None,
    ) -> None:
        self._router: ModelRouter = router
        self._run_config: RunConfig | None = run_config

    def build(self, problem: ProblemSpec) -> RunEvalDependencies:
        """Return a RunEvalDependencies with every collaborator instantiated."""
        rc = self._run_config or RunConfig()  # pure default (frozen config VO)
        ctx = WiringContext.create(self._router, rc)
        em = EmissionWiring(ctx).wire(problem)
        ta_deps = GenerateTestArchitectureDeps(
            gateway=ctx.gateway, router=ctx.router, toolkit=em.toolkit,
            recorder=ctx.recorder, run_config=rc,
        )
        techspec = TechSpecWiring()
        return RunEvalDependencies(
            design_architecture=DesignArchitecture(ctx.call_deps, ctx.loader),
            generate_test_architecture=GenerateTestArchitecture(ta_deps, ctx.loader),
            orchestrate_module=em.orchestrate_module,
            integrate_module=IntegrateModule(ctx.fs, em.adapters.bootstrap),
            validate_architecture=ValidateArchitecture(
                RuleRunnerFactory().build(em.adapters, em.toolkit),
                em.toolkit.file_extension,
            ),
            test_runner=em.adapters.test_runner,
            metric_collector=EvalMetricCollector(),
            functional_test_runner=em.adapters.functional_test_runner,
            llm_usage_recorder=ctx.recorder,
            review_security=ReviewSecurity(ctx.call_deps, ctx.loader),
            generate_security_tests=GenerateSecurityTests(ta_deps, ctx.loader),
            fix_failing_classes=FixFailingClasses(FixFailingClassesDeps(
                gateway=ctx.gateway, router=ctx.router, recorder=ctx.recorder,
                toolkit=em.toolkit, run_config=rc,
            )),
            file_system=ctx.fs,
            run_config=rc,
            cost_gate=ctx.cost_gate,
            sast_runner=BanditSastRunner(ctx.logger) if rc.enable_sast else None,
            model_router=ctx.router,
            run_logger=ctx.logger,
            verify_layer=(VerifyLayer(ctx.call_deps, ctx.loader)
                          if rc.verify_layers else None),
            tech_spec_resolver=techspec.resolver(rc, ctx.logger),
            infrastructure_choice_architect=techspec.choice_architect(
                rc, ctx.call_deps,
            ),
            dependency_installer=em.adapters.dependency_installer,
            project_compiler=LanguageCompilerFactory().for_language(
                problem.target_language
            ),
            test_repairer=RepairTestFile(ctx.gateway, ctx.router, rc, fs=ctx.fs),
            toolkit=em.toolkit,
            run_manifest=RunManifest(GitInfoAdapter(), ToolchainProbeAdapter()),
        )
