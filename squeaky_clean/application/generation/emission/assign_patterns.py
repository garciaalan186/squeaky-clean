"""AssignPatterns: build ClassAssignments for every class in a module."""

from pathlib import Path

from squeaky_clean.application.generation.emission.assign_patterns_paths import AssignPatternsPaths
from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.application.generation.emission.map_pattern_to_emitter import (
    MapPatternToEmitter,
)
from squeaky_clean.application.generation.emission.polymorphic_role_normalizer import (
    PolymorphicRoleNormalizer,
)
from squeaky_clean.application.generation.emission.routing.tier_c_icp_table import (
    CATEGORY_TO_ICP,
)
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.problem.custom_pattern_registry import (
    CustomPatternRegistry,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


class AssignPatterns:
    """Resolves a ModuleSpec to a tuple of ClassAssignments."""

    def __init__(
        self, toolkit: LanguageToolkit, output_root: Path,
        custom_patterns: CustomPatternRegistry | None = None,
        infrastructure_mode: str = "manual",
    ) -> None:
        self._toolkit = toolkit
        self._paths = AssignPatternsPaths(toolkit, output_root)
        self._mapper = MapPatternToEmitter(
            toolkit, infrastructure_mode=infrastructure_mode,
        )
        self._roles = PolymorphicRoleNormalizer()
        self._custom = custom_patterns or CustomPatternRegistry()  # pure default (in-memory)
        self._architecture: ArchitectureSpec | None = None
        self._tech_specs: dict[str, TechSpec] = {}

    def with_architecture(
        self, architecture: ArchitectureSpec | None,
    ) -> "AssignPatterns":
        self._architecture = architecture
        return self

    def register_tech_spec(self, spec: TechSpec) -> "AssignPatterns":
        self._tech_specs[spec.category] = spec
        self._mapper.register_category(spec.category)
        return self

    def assign_all(self, module: ModuleSpec) -> tuple[ClassAssignment, ...]:
        module = self._roles.normalize(module)
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
            emitter_spec_name=icp_name, file_path=str(src_path),
            test_file_path=str(test_path), architecture=self._architecture,
            tech_spec=self._tech_for(icp_name),
        )

    def _icp_for(self, c: ClassSpec, module: ModuleSpec) -> str:
        custom = self._custom.lookup(c.pattern)
        if custom is not None:
            return custom.emitter_spec_name
        return self._mapper.map_for(c, module)

    def _tech_for(self, icp_name: str) -> TechSpec | None:
        # Find the TechSpec whose category matches the routed Tier C ICP
        # (CATEGORY_TO_ICP is the one canonical table — R6.7).
        for cat, spec in self._tech_specs.items():
            if cat in CATEGORY_TO_ICP and CATEGORY_TO_ICP[cat] in icp_name:
                return spec
        return None
