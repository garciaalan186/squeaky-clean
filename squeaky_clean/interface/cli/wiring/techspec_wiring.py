"""TechSpecWiring: resolver + MCDA choice architect for --infra=auto runs."""

from pathlib import Path

from squeaky_clean.application.generation.techspec.infrastructure_choice_architect import (
    InfrastructureChoiceArchitect,
)
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.llm_call_deps import LLMCallDeps
from squeaky_clean.application.shared.mcda.mcda_registry import MCDARegistry
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.infrastructure.techspec.allowlist_loader import (
    load_allowlist_registry,
)
from squeaky_clean.infrastructure.techspec.composite_techspec_resolver import (
    CompositeTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.filesystem_techspec_resolver import (
    FilesystemTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)
from squeaky_clean.infrastructure.techspec.mcp_tech_doc_fetcher import MCPTechDocFetcher
from squeaky_clean.infrastructure.techspec.webfetch_tech_doc_fetcher import (
    WebFetchTechDocFetcher,
)

_FRAMEWORK_ROOT_DEPTH = 4


class TechSpecWiring:
    """Wires the H3/H4 techspec collaborators when --infra=auto."""

    def resolver(
        self, rc: RunConfig, logger: JSONLogger,
    ) -> TechSpecResolver | None:
        """Return the composite techspec resolver, or None when manual."""
        if rc.infrastructure_mode != "auto":
            return None
        eval_root = self._eval_root() / "tech_specs"
        schema_path = eval_root / "_schema.v1.json"
        if not schema_path.is_file():
            return None
        validator = JSONSchemaTechSpecValidator(schema_path)
        fs_resolver = FilesystemTechSpecResolver(
            eval_root, validator, run_logger=logger,
        )
        return CompositeTechSpecResolver(
            fs_resolver, validator,
            cache_root=eval_root / ".cache",
            ttl_days=rc.techspec_cache_ttl_days,
            mcp_fetcher=MCPTechDocFetcher(),
            web_fetcher=WebFetchTechDocFetcher(),
            allowlist_registry=load_allowlist_registry(eval_root),
            run_logger=logger,
        )

    def choice_architect(
        self, rc: RunConfig, call_deps: LLMCallDeps,
    ) -> InfrastructureChoiceArchitect | None:
        """Return the MCDA choice architect, or None when not inferred."""
        if rc.infrastructure_mode != "auto" or not rc.infer_infrastructure:
            return None
        scores_root = self._eval_root() / "mcda_scores"
        if not scores_root.is_dir():
            return None
        return InfrastructureChoiceArchitect(
            call_deps.gateway, MCDARegistry(scores_root),
            call_deps.router,
        )

    @staticmethod
    def _eval_root() -> Path:
        return Path(__file__).resolve().parents[_FRAMEWORK_ROOT_DEPTH] / "eval"
