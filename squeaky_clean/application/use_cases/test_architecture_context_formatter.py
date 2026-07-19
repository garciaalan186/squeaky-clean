"""TestArchitectureContextFormatter: render context into a user prompt string."""

from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.class_paths_block_renderer import (
    ClassPathsBlockRenderer,
)
from squeaky_clean.application.use_cases.dotted_class_path_resolver import (
    DottedClassPathResolver,
)
from squeaky_clean.application.use_cases.per_module_criterion_filter import (
    filter_criteria_for_module,
)
from squeaky_clean.application.use_cases.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class TestArchitectureContextFormatter:
    """Renders a TestArchitectureContext into the TestArchitect user prompt."""

    def __init__(self) -> None:
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._paths: ClassPathsBlockRenderer = ClassPathsBlockRenderer()

    def format(self, ctx: TestArchitectureContext) -> str:
        """Return a compact plain-text description of module + problem."""
        module = ctx.module
        problem = ctx.problem
        layered = self._is_layered(ctx)
        layer_slug = module.layer.value.lower()
        module_slug = self._snake.convert(module.name)
        test_dir = (
            f"tests/{layer_slug}/{module_slug}" if layered else "tests"
        )
        lines: list[str] = [
            f"Module: {module.name}",
            f"Layer: {module.layer.value}",
        ]
        if layered:
            lines.extend([
                f"LayerSlug: {layer_slug}",
                f"ModuleSlug: {module_slug}",
                f"TestDir: {test_dir}",
            ])
        lines.extend([
            f"ProblemId: {problem.id}",
            f"Description: {problem.description}",
        ])
        filtered = filter_criteria_for_module(
            problem.acceptance_criteria, module,
        )
        if filtered:
            lines.append("AcceptanceCriteria:")
            for crit in filtered:
                lines.append(f"  - {crit}")
        lines.extend(self._obligations_block(ctx))
        lines.append("Classes:")
        for cls in module.classes:
            lines.append(self._format_class(cls, module, layered, ctx))
        if layered and ctx.architecture is not None:
            extra = self._cross_module(module, ctx.architecture, ctx)
            if extra:
                lines.append("CrossModuleClasses:")
                lines.extend(extra)
        class_paths = self._paths.render(ctx)
        if class_paths:
            lines.append("ClassPaths:")
            lines.extend(class_paths)
        lines.append("")
        if layered:
            lines.append(
                f"FILE paths in TEST_SKELETONS MUST start with {test_dir}/ "
                f"(e.g. {test_dir}/test_<class>.py)."
            )
        lines.append(
            "Emit the GHERKIN and TEST_SKELETONS sections exactly as specified. "
            "No extra prose, no extra markdown."
        )
        return "\n".join(lines)

    def _obligations_block(
        self, ctx: TestArchitectureContext,
    ) -> list[str]:
        """The contract this module must discharge (rec 2/3/4/5).

        Infrastructure modules are integration-only (no unit tests). Other
        modules emit ONE test per projected obligation targeting one of their
        classes — narrowing generation to contract-bearing subjects and
        carrying the source criterion for traceability.
        """
        module = ctx.module
        if module.layer is LayerType.INFRASTRUCTURE:
            return ["Integration: this module's adapters require live "
                    "infrastructure. Emit ZERO tests here — the developer "
                    "owns integration tests for these classes."]
        if ctx.architecture is None:
            return []
        names = {c.name for c in module.classes}
        # Constructor-invariant duties are emitted deterministically elsewhere
        # (EmitInvariantTests); the LLM only writes behavioural criterion tests.
        mine = [o for o in ProjectTestObligations().project(
            ctx.architecture, ctx.problem)
            if o.target_class in names and o.method != "<init>"]
        if not mine:
            return []
        out = ["TestObligations (emit EXACTLY one test per line and ONLY "
               "these — do NOT add field-storage or happy-path tests; comment "
               "each test with its `from:` source):"]
        for o in mine:
            out.append(
                f"  - {o.target_class}.{o.method} must {o.kind.value} "
                f"({o.detail or 'the declared outcome'}) — from: {o.source}")
        return out

    def _is_layered(self, ctx: TestArchitectureContext) -> bool:
        return (
            ctx.toolkit is not None
            and ctx.toolkit.identifier_case == "snake"
        )

    def _format_class(
        self, cls: ClassSpec, module: ModuleSpec, layered: bool,
        ctx: TestArchitectureContext,
    ) -> str:
        fields = ", ".join(cls.fields) if cls.fields else ""
        methods = ", ".join(cls.methods) if cls.methods else ""
        prefix = (
            f"  - {cls.name} [{cls.pattern}] "
            f"fields=[{fields}] methods=[{methods}]"
        )
        if not layered:
            return prefix
        return f"{prefix} file={self._dotted(cls, module, ctx)}"

    def _cross_module(
        self, focal: ModuleSpec, arch: ArchitectureSpec,
        ctx: TestArchitectureContext,
    ) -> list[str]:
        out: list[str] = []
        for sibling in arch.modules:
            if sibling.name == focal.name:
                continue
            for cls in sibling.classes:
                if cls.name not in sibling.exports:
                    continue
                fields = ", ".join(cls.fields) if cls.fields else ""
                methods = ", ".join(cls.methods) if cls.methods else ""
                out.append(
                    f"  - {cls.name} [{cls.pattern}] "
                    f"fields=[{fields}] methods=[{methods}] "
                    f"file={self._dotted(cls, sibling, ctx)}"
                )
        return out

    def _dotted(
        self, cls: ClassSpec, module: ModuleSpec,
        ctx: TestArchitectureContext,
    ) -> str:
        if ctx.toolkit is not None:
            return DottedClassPathResolver(ctx.toolkit).resolve(cls, module)
        layer = module.layer.value.lower()
        mod_slug = self._snake.convert(module.name)
        stem = self._snake.convert(cls.name)
        return f"src.{layer}.{mod_slug}.{stem}"
