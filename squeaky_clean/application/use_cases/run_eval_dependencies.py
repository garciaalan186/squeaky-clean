"""RunEvalDependencies: bundled collaborators for RunEval.execute()."""

from dataclasses import dataclass, field

from squeaky_clean.application.use_cases.cost_gate import CostGate
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.use_cases.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.use_cases.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.use_cases.infrastructure_choice_architect import (
    InfrastructureChoiceArchitect,
)
from squeaky_clean.application.use_cases.integrate_module import IntegrateModule
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.application.use_cases.review_security import ReviewSecurity
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.application.use_cases.secret_path_scanner import SecretPathScanner
from squeaky_clean.application.use_cases.validate_architecture import ValidateArchitecture
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.metric_collector import MetricCollector
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.sast_runner import SastRunner
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.testing.test_runner import TestRunner


@dataclass(frozen=True)
class RunEvalDependencies:
    """Immutable bundle of every collaborator the RunEval use case needs.

    Bundling them into one frozen dataclass lets the RunEval constructor
    stay within the hard <=2-args rule (self excluded) while still
    wiring in the full collaborator graph. The CLI composition root
    is responsible for constructing this dependency graph.
    """

    design_architecture: DesignArchitecture
    generate_test_architecture: GenerateTestArchitecture
    orchestrate_module: OrchestrateModule
    integrate_module: IntegrateModule
    validate_architecture: ValidateArchitecture
    test_runner: TestRunner
    metric_collector: MetricCollector
    llm_usage_recorder: LLMUsageRecorder
    review_security: ReviewSecurity
    generate_security_tests: GenerateSecurityTests
    functional_test_runner: TestRunner | None = None
    fix_failing_classes: FixFailingClasses | None = None
    file_system: ProjectFileSystem | None = None
    run_config: RunConfig = field(default_factory=RunConfig)
    cost_gate: CostGate | None = None
    sast_runner: SastRunner | None = None
    secret_path_scanner: SecretPathScanner = field(default_factory=SecretPathScanner)
    model_router: ModelRouter = field(default_factory=ModelRouter)
    tech_spec_resolver: TechSpecResolver | None = None
    infrastructure_choice_architect: InfrastructureChoiceArchitect | None = None
    dependency_installer: DependencyInstaller | None = None
    project_compiler: ProjectCompiler | None = None
