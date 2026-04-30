"""GenerateTestArchitecture: ask the TestArchitect LLM for a TestArchitecture."""

from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.dtos.test_architecture_parse_error import (
    TestArchitectureParseError,
)
from squeaky_clean.application.use_cases.generate_test_architecture_deps import (
    GenerateTestArchitectureDeps,
)
from squeaky_clean.application.use_cases.generate_test_architecture_error import (
    GenerateTestArchitectureError,
)
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.parse_test_architecture import ParseTestArchitecture
from squeaky_clean.application.use_cases.test_architecture_context_formatter import (
    TestArchitectureContextFormatter,
)
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.model_tier import ModelTier


class GenerateTestArchitecture:
    """Use case: produce a TestArchitecture from a TestArchitectureContext via LLM."""

    def __init__(self, deps: GenerateTestArchitectureDeps) -> None:
        self._deps: GenerateTestArchitectureDeps = deps
        self._loader: LoadAgentSpec = LoadAgentSpec()
        self._parser: ParseTestArchitecture = ParseTestArchitecture()
        self._formatter: TestArchitectureContextFormatter = (
            TestArchitectureContextFormatter()
        )

    def execute(self, context: TestArchitectureContext) -> TestArchitecture:
        """Run the TestArchitect and return its parsed TestArchitecture."""
        spec_name = f"{self._deps.toolkit.architect_library}/TestArchitect"
        system_prompt = self._loader.load(spec_name)
        enriched = (
            context if context.toolkit is not None
            else TestArchitectureContext(
                module=context.module, problem=context.problem,
                toolkit=self._deps.toolkit,
            )
        )
        user_prompt = self._formatter.format(enriched)
        sampling = self._deps.run_config.sampling_for(ModelTier.MANAGER)
        request = LLMRequest(
            model=self._deps.router.route(ModelTier.MANAGER),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id,
            tier="manager",
        )
        response = self._deps.gateway.complete(request)
        self._deps.recorder.record(response, "test_architect")
        try:
            return self._parser.parse(response.content)
        except TestArchitectureParseError as exc:
            raise GenerateTestArchitectureError(
                f"TestArchitect produced unparseable output: {exc}"
            ) from exc
