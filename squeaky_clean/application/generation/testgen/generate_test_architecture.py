"""GenerateTestArchitecture: ask the TestArchitect LLM for a TestArchitecture."""

from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.testgen.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.generation.testgen.generate_test_architecture_error import (
    GenerateTestArchitectureError,
)
from squeaky_clean.application.generation.testgen.parse_test_architecture import (
    ParseTestArchitecture,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.generation.testgen.test_architecture_context_formatter import (
    TestArchitectureContextFormatter,
)
from squeaky_clean.application.generation.testgen.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.model_tier import ModelTier

# Test skeletons (esp. multi-file Java) overflow the gateway's 4096 default and
# truncate before the TEST_SKELETONS section — the root cause of Java runs
# failing with "missing ... section header". Give the tier headroom.
_MAX_OUTPUT_TOKENS: int = 8192
_MAX_RETRIES: int = 2
_RETRY_SUFFIX: str = (
    "\n\nRETRY: your previous output was rejected. Reason: {err}\n"
    "Emit BOTH sections IN FULL — a GHERKIN block then a TEST_SKELETONS block,"
    " each with its `---` rulers closed. If output is long, emit fewer, terser"
    " test files rather than truncating."
)
_TRUNCATED_ERR: str = "output was truncated at the token limit"


class GenerateTestArchitecture:
    """Use case: produce a TestArchitecture from a TestArchitectureContext via LLM."""

    def __init__(
        self, deps: GenerateTestArchitectureDeps,
        loader: LoadAgentSpec,
    ) -> None:
        self._deps: GenerateTestArchitectureDeps = deps
        self._loader: LoadAgentSpec = loader
        self._parser: ParseTestArchitecture = ParseTestArchitecture()
        self._formatter: TestArchitectureContextFormatter = (
            TestArchitectureContextFormatter()
        )

    def execute(self, context: TestArchitectureContext) -> TestArchitecture:
        """Run the TestArchitect, retrying with feedback on truncation/parse fail."""
        system_prompt = self._loader.load(
            f"{self._deps.toolkit.architect_library}/OracleCompiler"
        )
        base_prompt = self._formatter.format(self._enrich(context))
        last_err = ""
        for attempt in range(_MAX_RETRIES + 1):
            prompt = base_prompt if attempt == 0 else (
                base_prompt + _RETRY_SUFFIX.format(err=last_err)
            )
            response = self._deps.gateway.complete(self._request(system_prompt, prompt))
            self._deps.recorder.record(response, "test_architect")
            if response.truncated:
                last_err = _TRUNCATED_ERR
                continue
            try:
                return self._parser.parse(response.content)
            except TestArchitectureParseError as exc:
                last_err = str(exc)
        raise GenerateTestArchitectureError(
            f"TestArchitect produced unparseable output after "
            f"{_MAX_RETRIES + 1} attempts: {last_err}"
        )

    def _enrich(self, context: TestArchitectureContext) -> TestArchitectureContext:
        if context.toolkit is not None:
            return context
        return TestArchitectureContext(
            module=context.module, problem=context.problem,
            toolkit=self._deps.toolkit,
        )

    def _request(self, system_prompt: str, user_prompt: str) -> LLMRequest:
        sampling = self._deps.run_config.sampling_for(ModelTier.MANAGER)
        return LLMRequest(
            model=self._deps.router.route(ModelTier.MANAGER),
            system_prompt=system_prompt, user_prompt=user_prompt,
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id,
            tier="manager", max_tokens=_MAX_OUTPUT_TOKENS,
        )
