"""RepairTestFile: regenerate a test file to compile against the real source."""

import re

from squeaky_clean.application.generation.emission.dispatch.icp_execution_deps import (
    IcpExecutionDeps,
)
from squeaky_clean.application.generation.repair.repair_prompt_sources import (
    RepairPromptSources,
)

# Re-export: repair_obligation_gaps (owned by a parallel batch) still imports
# TestRepairRequest from this module; the class now lives in its own file.
from squeaky_clean.application.generation.repair.test_repair_request import (
    TestRepairRequest as TestRepairRequest,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_FENCE: re.Pattern[str] = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.DOTALL)
_SYSTEM: str = (
    "You repair a test file against the REAL source, which is AUTHORITATIVE. "
    "The instruction describes what is wrong: a COMPILE ERROR (fix the test "
    "to match the actual signatures) and/or undischarged TestObligations "
    "(ADD a test for each — e.g. 'construct X with violating input and assert "
    "it raises' means `with pytest.raises(...): X(bad)` / `assert.throws(() => "
    "new X(bad))` / `assertThrows(() -> new X(bad))`). KEEP every existing "
    "passing test, ADD what is missing, and never change the source or weaken "
    "an assertion's intent. Preserve the file's import style. To supply a "
    "value the code under test needs: for a "
    "first-party interface/abstract port, use a minimal in-test "
    "implementation; for a CONCRETE third-party/SDK class (e.g. a Spring "
    "KafkaTemplate), construct it with the library's real constructor or "
    "factory — NEVER anonymous-subclass a concrete class or invent a method "
    "with the wrong signature. Emit ONLY the corrected full test file in one "
    "fenced code block, no prose."
)


class RepairTestFile:
    """Single LLM call that rewrites one test file to match the real source."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRoutingPolicy,
        run_config: RunConfig | None = None, *, fs: ProjectFileSystem,
    ) -> None:
        self._deps = IcpExecutionDeps(
            gateway=gateway, router=router,
            run_config=run_config or RunConfig())
        self._fs: ProjectFileSystem = fs

    def repair(self, request: TestRepairRequest) -> LLMResponse | None:
        """Rewrite the test file in place; return the LLM response (or None)."""
        path = request.project_dir / request.rel_path
        try:
            current = path.read_text()
        except OSError:
            current = ""  # new file: the obligation has no test yet — create it
        response = self._deps.gateway.complete(self._request(request, current))
        match = _FENCE.search(response.content)
        if match is not None:
            fixed = match.group(1)
            if fixed.strip() and fixed != current:
                self._fs.write(path, fixed)
        return response

    def _request(self, req: TestRepairRequest, current: str) -> LLMRequest:
        sampling = self._deps.run_config.sampling_for(ModelTier.FIXER)
        return LLMRequest(
            model=self._deps.router.route(ModelTier.FIXER),
            system_prompt=_SYSTEM,
            user_prompt=self._prompt(req, current),
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id, tier="fixer",
        )

    def _prompt(self, req: TestRepairRequest, current: str) -> str:
        reader = RepairPromptSources()
        parts = [
            "SOURCE (authoritative — match these signatures):",
            reader.sources(req.project_dir, req.toolkit),
        ]
        exemplar = reader.exemplar(req.project_dir, req.rel_path)
        if exemplar:
            parts += ["", "TEST STYLE (match this test framework + import "
                      "style EXACTLY — same runner, same assertion library):",
                      f"```\n{exemplar}\n```"]
        parts += [
            "", "COMPILE ERRORS / OBLIGATIONS:",
            f"```\n{req.error_excerpt[:3000]}\n```",
            "", f"TEST FILE ({req.rel_path}) — emit a corrected version "
            "(if empty, create it):",
            f"```\n{current}\n```",
        ]
        return "\n".join(parts)
