"""RepairTestFile: regenerate a test file to compile against the real source."""

import re
from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.icp_execution_deps import IcpExecutionDeps
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_FENCE: re.Pattern[str] = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.DOTALL)
_SYSTEM: str = (
    "You repair a failing test so it compiles against the REAL source, "
    "which is AUTHORITATIVE. Fix the TEST to match the actual constructor "
    "and method signatures shown in SOURCE — never change the source, never "
    "weaken an assertion's intent. Preserve the scenarios and the file's "
    "imports style. Emit ONLY the corrected full test file in one fenced "
    "code block, no prose."
)


@dataclass(frozen=True)
class TestRepairRequest:
    """One test file to repair, with the diagnostics needed to fix it."""

    project_dir: Path
    rel_path: str
    error_excerpt: str
    toolkit: LanguageToolkit


class RepairTestFile:
    """Single LLM call that rewrites one test file to match the real source."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRouter,
        run_config: RunConfig | None = None,
    ) -> None:
        self._deps = IcpExecutionDeps(
            gateway=gateway, router=router,
            run_config=run_config or RunConfig())

    def repair(self, request: TestRepairRequest) -> LLMResponse | None:
        """Rewrite the test file in place; return the LLM response (or None)."""
        path = request.project_dir / request.rel_path
        try:
            current = path.read_text()
        except OSError:
            return None
        response = self._deps.gateway.complete(self._request(request, current))
        match = _FENCE.search(response.content)
        if match is not None:
            fixed = match.group(1)
            if fixed.strip() and fixed != current:
                path.write_text(fixed)
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
        return "\n".join([
            "SOURCE (authoritative — match these signatures):",
            self._sources(req.project_dir, req.toolkit),
            "", "COMPILE ERRORS:", f"```\n{req.error_excerpt[:3000]}\n```",
            "", f"TEST FILE ({req.rel_path}) — emit a corrected version:",
            f"```\n{current}\n```",
        ])

    @staticmethod
    def _sources(project_dir: Path, toolkit: LanguageToolkit) -> str:
        """Concatenate the production source files (excluding tests)."""
        ext = toolkit.file_extension
        out: list[str] = []
        for p in sorted(project_dir.rglob(f"*{ext}")):
            parts = p.parts
            if "test" in parts or "tests" in parts or p.name.endswith(f".test{ext}"):
                continue
            if "node_modules" in parts or "dist" in parts or "target" in parts:
                continue
            try:
                out.append(f"// {p.name}\n{p.read_text()}")
            except OSError:
                continue
        return "\n\n".join(out)[:12000]
