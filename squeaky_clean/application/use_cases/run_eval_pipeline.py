"""RunEvalPipeline: executes the architect->ICP->integrate->validate->pytest flow.

Multi-module aware: iterates `ArchitectureSpec.modules`, runs the
TestArchitect / SecurityArchitect per module, fans ICPs out via
`OrchestrateArchitecture`, then merges all module outputs into a single
flat `ModuleImplementation` + `TestArchitecture` for downstream
integration / metrics / test-run.
"""

from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.integration_request import IntegrationRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.application.dtos.security_test_context import SecurityTestContext
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.use_cases.architectural_complexity_scorer import (
    ArchitecturalComplexityScorer,
)
from squeaky_clean.application.use_cases.architecture_merger import ArchitectureMerger
from squeaky_clean.application.use_cases.budget_exit_handler import BudgetExitHandler
from squeaky_clean.application.use_cases.build_manifest_generator import (
    BuildManifestGenerator,
)
from squeaky_clean.application.use_cases.cargo_toml_generator import generate_cargo_toml
from squeaky_clean.application.use_cases.check_test_obligations import (
    CheckTestObligations,
)
from squeaky_clean.application.use_cases.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.use_cases.compile_gate import (
    CompileGate,
    CompileGateRequest,
    CompileGateResult,
)
from squeaky_clean.application.use_cases.contract_fidelity_error import (
    ContractFidelityError,
)
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry
from squeaky_clean.application.use_cases.cost_gate import BudgetExceededError
from squeaky_clean.application.use_cases.cross_module_dependency_error import (
    CrossModuleDependencyError,
)
from squeaky_clean.application.use_cases.derive_required_categories import (
    derive_required_categories,
)
from squeaky_clean.application.use_cases.fixer_stage import FixerStage, FixerStageResult
from squeaky_clean.application.use_cases.go_mod_generator import generate_go_mod
from squeaky_clean.application.use_cases.http_conventions_error import (
    HttpConventionsError,
)
from squeaky_clean.application.use_cases.metrics_inputs_assembler import (
    MetricsInputsAssembler,
)
from squeaky_clean.application.use_cases.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.application.use_cases.package_json_generator import (
    generate as generate_package_json,
)
from squeaky_clean.application.use_cases.per_module_criterion_filter import (
    filter_criteria_for_module,
)
from squeaky_clean.application.use_cases.percentile_summary_renderer import (
    PercentileSummaryRenderer,
)
from squeaky_clean.application.use_cases.pipeline_outputs import PipelineOutputs
from squeaky_clean.application.use_cases.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.application.use_cases.python_requirements_generator import (
    generate as generate_python_requirements,
)
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.use_cases.run_eval_metrics_builder import RunEvalMetricsBuilder
from squeaky_clean.application.use_cases.security_scan_stage import SecurityScanStage
from squeaky_clean.application.use_cases.select_infrastructure_choices import (
    select_infrastructure_choices,
)
from squeaky_clean.application.use_cases.spec_conformance_checker import (
    SpecConformanceChecker,
)
from squeaky_clean.application.use_cases.validate_architecture_against_spec import (
    SpecConformanceError,
    ValidateArchitectureAgainstSpec,
)
from squeaky_clean.application.use_cases.validate_contract_fidelity import (
    validate_contract_fidelity,
)
from squeaky_clean.application.use_cases.validate_cross_module_dependencies import (
    validate_cross_module_dependencies,
)
from squeaky_clean.application.use_cases.validate_dependency_injection import (
    validate_dependency_injection,
)
from squeaky_clean.application.use_cases.validate_http_conventions import (
    validate_http_conventions,
)
from squeaky_clean.application.use_cases.wiring_generator import WiringGenerator
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger


class RunEvalPipeline:
    """Sequences the full generate->integrate->validate->pytest flow."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps: RunEvalDependencies = deps
        self._builder: RunEvalMetricsBuilder = RunEvalMetricsBuilder()
        self._assembler: MetricsInputsAssembler = MetricsInputsAssembler(
            deps.llm_usage_recorder, deps.model_router,
        )
        self._fixer: FixerStage = FixerStage(
            deps.fix_failing_classes, deps.file_system,
        )
        self._compile_gate: CompileGate = CompileGate(
            deps.project_compiler, self._fixer, deps.test_repairer,
        )
        self._merger: ArchitectureMerger = ArchitectureMerger()
        self._orchestrator: OrchestrateArchitecture = OrchestrateArchitecture(
            deps.orchestrate_module,
        )
        self._spec_validator: ValidateArchitectureAgainstSpec = (
            ValidateArchitectureAgainstSpec()
        )
        self._budget_exit: BudgetExitHandler = BudgetExitHandler(deps.cost_gate)
        self._security: SecurityScanStage = SecurityScanStage(
            deps.secret_path_scanner, deps.sast_runner,
        )
        self._logger: JSONLogger = JSONLogger()
        self._contracts: ContractRegistry = ContractRegistry()
        self._wiring: WiringGenerator = WiringGenerator()
        self._build_manifest: BuildManifestGenerator = BuildManifestGenerator()
        self._tech_specs_by_category: dict[str, TechSpec] = {}
        self._infra_explicit: int = 0
        self._infra_derived: int = 0
        self._mcda_runs: int = 0
        self._dep_install_failed: bool = False
        self._http_violations: int = 0
        self._di_violations: int = 0
        self._architect_retries: int = 0
        self._test_criteria_filtered: int = 0
        self._arch: ArchitectureSpec | None = None

    def run(self, problem: ProblemSpec, output_dir: Path) -> EvalReportBundle:
        """Execute the full pipeline; on budget exit produce a partial report."""
        try:
            return self._run_to_completion(problem, output_dir)
        except BudgetExceededError as exc:
            return self._budget_exit.handle(problem, output_dir, exc)

    def _run_to_completion(
        self, problem: ProblemSpec, output_dir: Path,
    ) -> EvalReportBundle:
        d = self._deps
        emitter = CheckpointEmitter(problem.id, output_dir)
        arch = d.design_architecture.execute(problem)
        arch = self._check_dependency_injection(arch, problem)
        self._arch = arch
        self._persist_notation(output_dir)
        emitter.architect_done(d.design_architecture.last_raw_notation)
        self._check_cross_module_deps(arch, output_dir)
        spec_violations = self._spec_validator.execute(arch, problem)
        if spec_violations:
            raise SpecConformanceError(
                f"architecture violates ProblemSpec semantics: {spec_violations}"
            )
        arch = self._check_http_conventions(arch, problem, output_dir)
        self._check_contract_fidelity(arch, problem, output_dir)
        test_arch = self._merge_test_architectures(arch, problem)
        sec_arch = self._merge_security_test_architectures(arch, problem)
        emitter.test_arch_done(test_arch, sec_arch)
        self._resolve_tech_specs(problem, arch)
        module_impls = self._orchestrator.execute(arch)
        emitter.icps_done(module_impls)
        impl = self._merger.merge_implementations(arch, module_impls)
        d.integrate_module.execute(IntegrationRequest(
            implementation=impl, test_architecture=test_arch,
            output_dir=output_dir, security_test_architecture=sec_arch))
        emitter.integrated()
        self._maybe_emit_wiring(arch, output_dir)
        self._maybe_emit_build_manifest(arch, problem, output_dir)
        validation = d.validate_architecture.execute(output_dir)
        self._install_deps(output_dir)
        compile_result = self._run_compile_gate(impl, output_dir)
        test_run = d.test_runner.run(output_dir)
        emitter.tested()
        test_run, fix_stats = self._run_fixer_loop(impl, test_run, output_dir)
        fix_stats = fix_stats.merge(compile_result.fixer)
        emitter.fixed(fix_stats.passes)
        func_run = (d.functional_test_runner.run(output_dir)
                    if d.functional_test_runner else None)
        outputs = PipelineOutputs(
            implementation=impl, test_run=test_run, validation=validation,
            func_run=func_run, security_architecture=sec_arch,
            fix_stats=fix_stats,
        )
        inputs = self._assembler.assemble(outputs, output_dir)
        metrics = self._builder.build(inputs)
        metrics.infrastructure_choices_explicit = self._infra_explicit
        metrics.infrastructure_choices_derived = self._infra_derived
        metrics.mcda_runs = self._mcda_runs
        metrics.infrastructure_icp_count = self._count_infra_icps(module_impls)
        metrics.dependency_install_failed = self._dep_install_failed
        metrics.http_convention_violations = self._http_violations
        metrics.architect_retries = self._architect_retries
        metrics.test_criteria_filtered = self._test_criteria_filtered
        metrics.compile_errors = compile_result.compile_errors
        metrics.spec_conformance_violations = len(
            SpecConformanceChecker().check(impl)
        )
        metrics.test_obligation_gaps = self._obligation_gaps(problem, output_dir)
        metrics.dependency_injection_violations = self._di_violations
        self._security.apply(
            output_dir, metrics, self._deps.run_config.enable_sast,
        )
        self._populate_acs(arch, problem, output_dir, metrics)
        self._write_percentiles(output_dir)
        self._register_produced(problem)
        emitter.complete(metrics.estimated_cost_usd)
        return EvalReportBundle(
            problem=problem, metrics=metrics,
            test_run_result=test_run, validation=validation,
        )

    def _merge_test_architectures(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> TestArchitecture:
        per_module: list[TestArchitecture] = []
        for m in arch.modules:
            kept = filter_criteria_for_module(
                problem.acceptance_criteria, m,
            )
            self._test_criteria_filtered += (
                len(problem.acceptance_criteria) - len(kept)
            )
            per_module.append(self._deps.generate_test_architecture.execute(
                TestArchitectureContext(
                    module=m, problem=problem, architecture=arch,
                ),
            ))
        return self._merger.merge_test_architectures(per_module)

    def _merge_security_test_architectures(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> TestArchitecture:
        per_module: list[TestArchitecture] = []
        for m in arch.modules:
            review = self._deps.review_security.execute(
                SecurityReviewContext(module=m, problem=problem),
            )
            per_module.append(self._deps.generate_security_tests.execute(
                SecurityTestContext(
                    review=review, module=m, problem=problem,
                    architecture=arch,
                ),
            ))
        return self._merger.merge_test_architectures(per_module)

    def _obligation_gaps(
        self, problem: ProblemSpec, output_dir: Path,
    ) -> int:
        """Deterministic count of spec obligations no generated test discharges."""
        if self._arch is None:
            return 0
        obligations = ProjectTestObligations().project(self._arch, problem)
        return len(CheckTestObligations().check(obligations, output_dir))

    def _run_compile_gate(
        self, impl: ModuleImplementation, output_dir: Path,
    ) -> CompileGateResult:
        """Compile before tests; fix implicated source classes on failure."""
        return self._compile_gate.run(CompileGateRequest(
            implementation=impl, output_dir=output_dir,
            max_passes=self._max_fixer_passes(), architecture=self._arch,
            toolkit=self._deps.toolkit,
        ))

    def _run_fixer_loop(
        self, impl: ModuleImplementation, test_run: TestRunResult,
        output_dir: Path,
    ) -> tuple[TestRunResult, FixerStageResult]:
        """Run FixerStage up to ``max_fixer_passes`` times until tests pass."""
        d = self._deps
        max_passes = self._max_fixer_passes()
        agg = FixerStageResult(0, 0, 0, 0.0, 0, 0)
        cur_run = test_run
        for _ in range(max_passes):
            if cur_run.failed == 0 and cur_run.errors == 0:
                break
            stats = self._fixer.apply(
                FixRequest(implementation=impl, test_run_result=cur_run,
                           architecture=self._arch),
                output_dir,
            )
            agg = agg.merge(stats)
            if stats.classes_fixed == 0:
                break
            cur_run = d.test_runner.run(output_dir)
        return cur_run, agg

    def _max_fixer_passes(self) -> int:
        return int(self._deps.run_config.retry_policy.max_fixer_passes)

    def _persist_notation(self, output_dir: Path) -> None:
        path = output_dir / "architecture.notation"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._deps.design_architecture.last_raw_notation)

    def _write_percentiles(self, output_dir: Path) -> None:
        """Write per-tier latency + cost percentiles to LATENCY_PERCENTILES.md."""
        section = PercentileSummaryRenderer().render(self._deps.llm_usage_recorder)
        if not section:
            return
        try:
            (output_dir / "LATENCY_PERCENTILES.md").write_text(section)
        except OSError:
            pass

    def _populate_acs(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
        output_dir: Path, metrics: EvalMetrics,
    ) -> None:
        """Compute Architectural Complexity Score + normalized derivatives."""
        score = ArchitecturalComplexityScorer().score(
            problem, arch, output_dir / "src",
        )
        metrics.acs_structural = score.structural
        metrics.acs_codegen = score.codegen
        metrics.acs_constraint = score.constraint
        metrics.acs_composite = score.composite
        metrics.acs_normalized = score.normalized
        if score.composite > 0:
            metrics.acs_cost_per_unit = round(
                metrics.estimated_cost_usd / score.composite, 4,
            )
            wall_s = max(metrics.total_wall_clock_ms / 1000.0, 0.001)
            metrics.acs_velocity = round(score.composite / wall_s, 3)

    def _resolve_tech_specs(
        self, problem: ProblemSpec, arch: ArchitectureSpec,
    ) -> None:
        """H1+H3: resolve TechSpecs (explicit + optional MCDA-derived)."""
        if self._deps.run_config.infrastructure_mode != "auto":
            return
        resolver = self._deps.tech_spec_resolver
        if resolver is None:
            return
        infer = self._deps.run_config.infer_infrastructure
        explicit_count = len(problem.infrastructure_choices)
        required = derive_required_categories(arch) if infer else frozenset()
        choices = select_infrastructure_choices(
            problem, required, infer,
            self._deps.infrastructure_choice_architect,
        ) if (infer or problem.infrastructure_choices) else ()
        if not choices:
            return
        derived_count = max(0, len(choices) - explicit_count)
        self._infra_explicit = explicit_count
        self._infra_derived = derived_count
        self._mcda_runs = derived_count
        specs = tuple(
            resolver.resolve(c.category, c.technology, c.version_pin)
            for c in choices
        )
        self._orchestrator.register_tech_specs(specs)
        self._tech_specs_by_category = {s.category: s for s in specs}

    @staticmethod
    def _count_infra_icps(
        module_impls: tuple[ModuleImplementation, ...],
    ) -> int:
        """Count classes whose module is in the Infrastructure layer."""
        from squeaky_clean.domain.value_objects.layer_type import LayerType
        return sum(
            len(m.implemented_classes) for m in module_impls
            if m.module.layer is LayerType.INFRASTRUCTURE
        )

    def _check_cross_module_deps(
        self, arch: ArchitectureSpec, output_dir: Path,
    ) -> None:
        violations = validate_cross_module_dependencies(arch)
        if not violations:
            return
        for v in violations:
            self._logger.event("cross_module_violation", message=v)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "CROSS_MODULE_VIOLATIONS.txt").write_text(
            "\n".join(violations) + "\n"
        )
        raise CrossModuleDependencyError(violations)

    def _check_http_conventions(
        self, arch: ArchitectureSpec, problem: ProblemSpec, output_dir: Path,
    ) -> ArchitectureSpec:
        """Enforce constraint #22; retry architect once, then abort."""
        violations = validate_http_conventions(arch, problem)
        if not violations:
            return arch
        self._http_violations = len(violations)
        for v in violations:
            self._logger.event("http_convention_violation", message=v)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "HTTP_CONVENTION_VIOLATIONS.txt").write_text(
            "\n".join(violations) + "\n"
        )
        self._architect_retries += 1
        retry_arch = self._deps.design_architecture.execute(
            problem, prior_violations=violations,
        )
        retry_violations = validate_http_conventions(retry_arch, problem)
        if retry_violations:
            self._http_violations = len(retry_violations)
            (output_dir / "HTTP_CONVENTION_VIOLATIONS.txt").write_text(
                "\n".join(retry_violations) + "\n"
            )
            raise HttpConventionsError(retry_violations)
        self._http_violations = 0
        return retry_arch

    def _check_dependency_injection(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> ArchitectureSpec:
        """Deterministic gate: make an orchestrator's injected port explicit.

        Detect a UseCase/Facade that declares no fields yet must inject a
        same-module port, then re-ask the architect with that specific
        feedback. Non-fatal: a retry that raises, is structurally invalid,
        or does not reduce the violations is discarded for the original.
        """
        violations = validate_dependency_injection(arch)
        self._di_violations = len(violations)
        if not violations:
            return arch
        for v in violations:
            self._logger.event("dependency_injection_violation", message=v)
        self._architect_retries += 1
        try:
            retry = self._deps.design_architecture.execute(
                problem, prior_violations=violations)
        except Exception as exc:  # noqa: BLE001
            self._logger.event("di_retry_error", error=str(exc))
            return arch
        if validate_cross_module_dependencies(retry):
            self._logger.event("di_retry_discarded", reason="cross_module")
            return arch
        retry_violations = validate_dependency_injection(retry)
        if len(retry_violations) < len(violations):
            self._di_violations = len(retry_violations)
            return retry
        self._logger.event("di_retry_discarded", reason="no_improvement")
        return arch

    def _check_contract_fidelity(
        self, arch: ArchitectureSpec, problem: ProblemSpec, output_dir: Path,
    ) -> None:
        violations = validate_contract_fidelity(arch, problem, self._contracts)
        if not violations:
            return
        for v in violations:
            self._logger.event("contract_fidelity_violation", message=v)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "CONTRACT_FIDELITY_VIOLATIONS.txt").write_text(
            "\n".join(violations) + "\n")
        raise ContractFidelityError(violations)

    def _register_produced(self, problem: ProblemSpec) -> None:
        for c in problem.produces_contracts:
            stamped = c if c.producer_problem_id else type(c)(
                name=c.name, transport=c.transport, fields=c.fields,
                producer_problem_id=problem.id)
            try:
                self._contracts.register(stamped)
            except OSError as exc:
                self._logger.event(
                    "contract_register_failed",
                    contract=c.name, error=str(exc))

    def _maybe_emit_wiring(
        self, arch: ArchitectureSpec, output_dir: Path,
    ) -> None:
        cfg = self._deps.run_config
        if cfg.infrastructure_mode != "auto" or not cfg.emit_wiring:
            return
        try:
            path = self._wiring.generate(
                arch, self._tech_specs_by_category, output_dir)
            self._logger.event("wiring_emitted", path=str(path))
        except OSError as exc:
            self._logger.event("wiring_emit_failed", error=str(exc))

    def _maybe_emit_build_manifest(
        self, arch: ArchitectureSpec, problem: ProblemSpec, output_dir: Path,
    ) -> None:
        cfg = self._deps.run_config
        if cfg.infrastructure_mode != "auto":
            return
        try:
            path = self._build_manifest.generate(
                arch, self._tech_specs_by_category, output_dir, problem)
            if path is not None:
                self._logger.event("build_manifest_emitted", path=str(path))
        except OSError as exc:
            self._logger.event("build_manifest_emit_failed", error=str(exc))
        try:
            go_path = generate_go_mod(
                arch, self._tech_specs_by_category, output_dir, problem)
            if go_path is not None:
                self._logger.event("go_mod_emitted", path=str(go_path))
        except OSError as exc:
            self._logger.event("go_mod_emit_failed", error=str(exc))
        try:
            cargo_path = generate_cargo_toml(
                arch, self._tech_specs_by_category, output_dir, problem)
            if cargo_path is not None:
                self._logger.event("cargo_toml_emitted", path=str(cargo_path))
        except OSError as exc:
            self._logger.event("cargo_toml_emit_failed", error=str(exc))
        self._maybe_emit_python_or_npm_manifest(arch, problem, output_dir)

    def _maybe_emit_python_or_npm_manifest(
        self, arch: ArchitectureSpec, problem: ProblemSpec, output_dir: Path,
    ) -> None:
        from squeaky_clean.domain.value_objects.target_language import TargetLanguage
        lang = problem.target_language
        try:
            if lang is TargetLanguage.PYTHON:
                req_path = generate_python_requirements(
                    arch, self._tech_specs_by_category, output_dir, problem)
                if req_path is not None:
                    self._logger.event(
                        "requirements_txt_emitted", path=str(req_path))
            elif lang in (TargetLanguage.JAVASCRIPT, TargetLanguage.TYPESCRIPT):
                pkg_path = generate_package_json(
                    arch, self._tech_specs_by_category, output_dir, problem)
                if pkg_path is not None:
                    self._logger.event(
                        "package_json_emitted", path=str(pkg_path))
        except OSError as exc:
            self._logger.event("manifest_emit_failed", error=str(exc))

    def _install_deps(self, output_dir: Path) -> None:
        """Run the language-specific dependency installer before tests."""
        installer = self._deps.dependency_installer
        if installer is None:
            return
        result = installer.install(output_dir)
        self._dep_install_failed = not result.succeeded
        self._logger.event(
            "dependency_install",
            succeeded=result.succeeded, duration_ms=result.duration_ms,
            message=result.message[:500],
        )
