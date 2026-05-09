"""MetricsInputsAssembler: build MetricsInputs from a PipelineOutputs snapshot."""

from pathlib import Path

from squeaky_clean.application.dtos.metrics_inputs import MetricsInputs
from squeaky_clean.application.use_cases.file_stats_scanner import FileStatsScanner
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.pipeline_outputs import PipelineOutputs
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class MetricsInputsAssembler:
    """Turns a PipelineOutputs snapshot + recorder stats into MetricsInputs."""

    def __init__(
        self, recorder: LLMUsageRecorder, router: ModelRouter | None = None,
    ) -> None:
        self._recorder: LLMUsageRecorder = recorder
        self._scanner: FileStatsScanner = FileStatsScanner()
        self._router: ModelRouter = router if router is not None else ModelRouter()

    def assemble(
        self, outputs: PipelineOutputs, output_dir: Path,
    ) -> MetricsInputs:
        """Return a MetricsInputs DTO ready for RunEvalMetricsBuilder."""
        impl = outputs.implementation
        a = self._recorder.stats("architect")
        t = self._recorder.stats("test_architect")
        sa = self._recorder.stats("security_architect")
        sta = self._recorder.stats("security_icp")
        f = outputs.fix_stats
        hits, misses, ctok, rtok = self._recorder.cache_stats()
        ac, ar = self._recorder.tier_cache_stats("architect")
        mc, mr = self._recorder.tier_cache_stats("manager")
        ic, ir = self._recorder.tier_cache_stats("icp")
        fc, fr = self._recorder.tier_cache_stats("fixer")
        return MetricsInputs(
            implementation=impl, test_run_result=outputs.test_run,
            validation=outputs.validation,
            functional_test_run_result=outputs.func_run,
            agent_retries=impl.total_retries,
            security_test_count=len(outputs.security_architecture.test_skeletons),
            icp_input_tokens=impl.total_input_tokens,
            icp_output_tokens=impl.total_output_tokens,
            icp_cost_usd=impl.total_cost_usd,
            icp_duration_ms=impl.total_duration_ms,
            icp_wall_duration_ms=impl.wall_duration_ms,
            file_stats=self._scanner.scan(output_dir),
            architect_input_tokens=a[0], architect_output_tokens=a[1],
            architect_cost_usd=a[2], architect_duration_ms=a[3],
            test_architect_input_tokens=t[0], test_architect_output_tokens=t[1],
            test_architect_cost_usd=t[2], test_architect_duration_ms=t[3],
            security_architect_input_tokens=sa[0] + sta[0],
            security_architect_output_tokens=sa[1] + sta[1],
            security_architect_cost_usd=sa[2] + sta[2],
            security_architect_duration_ms=sa[3] + sta[3],
            classes_fixed=f.classes_fixed,
            fixer_input_tokens=f.input_tokens,
            fixer_output_tokens=f.output_tokens,
            fixer_cost_usd=f.cost_usd,
            fixer_duration_ms=f.duration_ms,
            cache_hit_count=hits, cache_miss_count=misses,
            cache_creation_input_tokens=ctok, cache_read_input_tokens=rtok,
            llm_timeouts=self._recorder.timeout_count(),
            cache_create_architect_tokens=ac, cache_read_architect_tokens=ar,
            cache_create_manager_tokens=mc, cache_read_manager_tokens=mr,
            cache_create_icp_tokens=ic, cache_read_icp_tokens=ir,
            cache_create_fixer_tokens=fc, cache_read_fixer_tokens=fr,
            architect_model=self._router.route(ModelTier.ARCHITECT),
            manager_model=self._router.route(ModelTier.MANAGER),
            icp_model=self._router.route(ModelTier.ICP),
            fixer_model=self._router.route(ModelTier.FIXER),
            composer_validation_failures=outputs.composer_stats.validation_failures,
            composer_manager_fallback_calls=outputs.composer_stats.manager_fallback_calls,
        )
