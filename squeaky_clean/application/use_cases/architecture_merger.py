"""ArchitectureMerger: collapse N module impls + test architectures into one bundle.

The downstream pipeline (IntegrateModule, MetricsInputsAssembler) is
single-module-shaped. This merger preserves backward-compat by combining
all per-module ICP outputs into a synthetic flat ModuleImplementation +
TestArchitecture pair, suitable for single-pass integration.
"""

from __future__ import annotations

from collections.abc import Sequence

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class ArchitectureMerger:
    """Reduce multi-module pipeline outputs to single-shape DTOs."""

    def merge_implementations(
        self,
        arch: ArchitectureSpec,
        impls: Sequence[ModuleImplementation],
    ) -> ModuleImplementation:
        """Concatenate every module's classes; sum token/cost/duration."""
        all_classes: list[ImplementedClass] = []
        for impl in impls:
            all_classes.extend(impl.implemented_classes)
        return ModuleImplementation(
            module=self._merged_module(arch),
            implemented_classes=tuple(all_classes),
            total_cost_usd=sum(i.total_cost_usd for i in impls),
            total_duration_ms=sum(i.total_duration_ms for i in impls),
            total_input_tokens=sum(i.total_input_tokens for i in impls),
            total_output_tokens=sum(i.total_output_tokens for i in impls),
            wall_duration_ms=max((i.wall_duration_ms for i in impls), default=0),
            total_retries=sum(i.total_retries for i in impls),
        )

    def merge_test_architectures(
        self,
        archs: Sequence[TestArchitecture],
    ) -> TestArchitecture:
        """Concatenate scenarios and skeletons across modules."""
        scenarios: list[str] = []
        skeletons: list[TestSkeleton] = []
        for ta in archs:
            scenarios.extend(ta.gherkin_scenarios)
            skeletons.extend(ta.test_skeletons)
        return TestArchitecture(
            gherkin_scenarios=tuple(scenarios),
            test_skeletons=tuple(skeletons),
        )

    def _merged_module(self, arch: ArchitectureSpec) -> ModuleSpec:
        """Synthetic ModuleSpec carrying every module's classes flattened."""
        all_classes: list[ClassSpec] = []
        for m in arch.modules:
            all_classes.extend(m.classes)
        return ModuleSpec(
            name=arch.modules[0].name if arch.modules else "Architecture",
            layer=arch.modules[0].layer if arch.modules else LayerType.DOMAIN,
            exports=tuple(
                e for m in arch.modules for e in m.exports
            ),
            depends=(),
            classes=tuple(all_classes),
            invariants=tuple(
                inv for m in arch.modules for inv in m.invariants
            ),
        )
