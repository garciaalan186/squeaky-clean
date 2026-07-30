"""VerifyLayer: optional LLM pass that audits one module against its layer spec."""

from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.recovery.squib.squib_module_writer import (
    SquibModuleWriter,
)
from squeaky_clean.application.shared.gateways.llm_call_deps import LLMCallDeps
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_SPEC_FOR: dict[LayerType, str] = {
    LayerType.DOMAIN: "DomainVerifier",
    LayerType.APPLICATION: "ApplicationVerifier",
    LayerType.INFRASTRUCTURE: "InfrastructureVerifier",
    LayerType.INTERFACE: "InterfaceVerifier",
}


class VerifyLayer:
    """Runs the per-layer Verifier agent over a ModuleSpec (opt-in).

    Wired behind ``RunConfig.verify_layers`` (default off): the four
    ``*Verifier.md`` specs are a Manager-tier second opinion on top of the
    mechanical ``arch.validate()`` + DependencyRule checks. Returns the parsed
    ``VIOLATION:`` lines (empty when the layer reports ``OK``).
    """

    def __init__(
        self, deps: LLMCallDeps, loader: LoadAgentSpec | None = None,
    ) -> None:
        self._deps: LLMCallDeps = deps
        self._loader: LoadAgentSpec = loader or LoadAgentSpec()
        self._writer: SquibModuleWriter = SquibModuleWriter()

    def verify(self, module: ModuleSpec) -> tuple[str, ...]:
        """Return the verifier's VIOLATION lines for ``module`` (empty if OK)."""
        system = self._loader.load(_SPEC_FOR[module.layer])
        request = LLMRequest(
            model=self._deps.router.route(ModelTier.MANAGER),
            system_prompt=system, user_prompt=self._writer.write(module),
            tier="manager",
        )
        response = self._deps.gateway.complete(request)
        self._deps.recorder.record(response, "manager")
        return self._parse(response.content)

    @staticmethod
    def _parse(content: str) -> tuple[str, ...]:
        return tuple(
            line.split("VIOLATION:", 1)[1].strip()
            for line in content.splitlines()
            if line.strip().startswith("VIOLATION:")
        )
