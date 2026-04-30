"""AssignPatterns: build ClassAssignments for every class in a module."""

from pathlib import Path

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.assign_patterns_paths import AssignPatternsPaths
from squeaky_clean.application.use_cases.custom_pattern_registry import (
    CustomPatternRegistry,
)
from squeaky_clean.application.use_cases.map_pattern_to_icp import MapPatternToICP
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


def _method_names(c: ClassSpec) -> tuple[str, ...]:
    return tuple(m.split("(", 1)[0].strip() for m in c.methods if m.strip())


class AssignPatterns:
    """Resolves a ModuleSpec to a tuple of ClassAssignments."""

    def __init__(
        self, toolkit: LanguageToolkit, output_root: Path,
        custom_patterns: CustomPatternRegistry | None = None,
        infrastructure_mode: str = "manual",
    ) -> None:
        self._toolkit = toolkit
        self._paths = AssignPatternsPaths(toolkit, output_root)
        self._mapper = MapPatternToICP()
        self._custom = custom_patterns or CustomPatternRegistry()
        self._architecture: ArchitectureSpec | None = None
        self._infra_mode = infrastructure_mode
        self._tech_specs: dict[str, TechSpec] = {}

    def with_architecture(
        self, architecture: ArchitectureSpec | None,
    ) -> "AssignPatterns":
        self._architecture = architecture
        return self

    def register_tech_spec(self, spec: TechSpec) -> "AssignPatterns":
        self._tech_specs[spec.category] = spec
        return self

    def assign_all(self, module: ModuleSpec) -> tuple[ClassAssignment, ...]:
        return tuple(self._one(cls, module) for cls in module.classes)

    def tier_c_class_names(self, module: ModuleSpec) -> frozenset[str]:
        """Names of classes in ``module`` that route to a Tier C ICP."""
        return frozenset(
            cls.name for cls in module.classes
            if "infrastructure/" in self._icp_for(cls, module)
        )

    def _one(self, c: ClassSpec, module: ModuleSpec) -> ClassAssignment:
        icp_name = self._icp_for(c, module)
        src_path, test_path = self._paths.for_class(c.name, module)
        return ClassAssignment(
            class_spec=c, module=module, toolkit=self._toolkit,
            icp_spec_name=icp_name, file_path=str(src_path),
            test_file_path=str(test_path), architecture=self._architecture,
            tech_spec=self._tech_for(icp_name),
        )

    def _icp_for(self, c: ClassSpec, module: ModuleSpec) -> str:
        custom = self._custom.lookup(c.pattern)
        if custom is not None:
            return custom.icp_spec_name
        return self._mapper.map_with_layer(
            c.pattern, self._toolkit, module.layer,
            _method_names(c), infrastructure_mode=self._infra_mode,
            declared_categories=tuple(self._tech_specs.keys()),
        )

    def _tech_for(self, icp_name: str) -> TechSpec | None:
        # Find the TechSpec whose category matches the routed Tier C ICP.
        for cat, spec in self._tech_specs.items():
            if cat in _CATEGORY_TO_ICP_SUFFIX and (
                _CATEGORY_TO_ICP_SUFFIX[cat] in icp_name
            ):
                return spec
        return None


_CATEGORY_TO_ICP_SUFFIX: dict[str, str] = {
    "blob_storage": "BlobStorageAdapterICP",
    "kv_cache": "KvCacheICP",
    "rest_client": "RestClientICP",
    "relational_db": "RelationalDBRepositoryICP",
    "document_db": "DocumentDBRepositoryICP",
    "message_queue_producer": "MessageQueueProducerICP",
    "message_queue_consumer": "MessageQueueConsumerICP",
    "stream_processor": "StreamProcessorICP",
    "rest_server_handler": "RestServerHandlerICP",
    "grpc_client": "GrpcClientICP",
    "grpc_server_handler": "GrpcServerHandlerICP",
    "websocket_server_handler": "WebSocketServerHandlerICP",
    "observability_logger": "ObservabilityLoggerICP",
    "secrets_provider": "SecretsProviderICP",
    "search": "SearchICP",
}
