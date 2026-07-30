"""RunEvalDependencies: bundled collaborators for RunEval.execute()."""

from dataclasses import dataclass, field

from squeaky_clean.application.generation.architecture.design_architecture import DesignArchitecture
from squeaky_clean.application.generation.emission.orchestrate_module import OrchestrateModule
from squeaky_clean.application.generation.integration.integrate_module import IntegrateModule
from squeaky_clean.application.generation.repair.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.generation.repair.repair_test_file import RepairTestFile
from squeaky_clean.application.generation.security.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.generation.security.review_security import ReviewSecurity
from squeaky_clean.application.generation.security.secret_path_scanner import SecretPathScanner
from squeaky_clean.application.generation.techspec.infrastructure_choice_architect import (
    InfrastructureChoiceArchitect,
)
from squeaky_clean.application.generation.testgen.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.generation.validation.validate_architecture import (
    ValidateArchitecture,
)
from squeaky_clean.application.generation.validation.verify_layer import VerifyLayer
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.metric_collector import MetricCollector
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.interfaces.sast_runner import SastRunner
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.domain.interfaces.test_runner import TestRunner


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
    model_router: ModelRoutingPolicy
    functional_test_runner: TestRunner | None = None
    fix_failing_classes: FixFailingClasses | None = None
    file_system: ProjectFileSystem | None = None
    run_config: RunConfig = field(default_factory=RunConfig)
    cost_gate: CostGate | None = None
    sast_runner: SastRunner | None = None
    secret_path_scanner: SecretPathScanner = field(default_factory=SecretPathScanner)
    run_logger: RunLogger = field(default_factory=NullRunLogger)
    verify_layer: VerifyLayer | None = None
    tech_spec_resolver: TechSpecResolver | None = None
    infrastructure_choice_architect: InfrastructureChoiceArchitect | None = None
    dependency_installer: DependencyInstaller | None = None
    project_compiler: ProjectCompiler | None = None
    test_repairer: RepairTestFile | None = None
    toolkit: LanguageToolkit | None = None
