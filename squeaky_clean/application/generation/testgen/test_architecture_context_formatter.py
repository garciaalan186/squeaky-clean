"""TestArchitectureContextFormatter: render context into a user prompt string."""

from squeaky_clean.application.generation.emission.class_paths_block_renderer import (
    ClassPathsBlockRenderer,
)
from squeaky_clean.application.generation.testgen.prompting.class_line_renderer import (
    ClassLineRenderer,
)
from squeaky_clean.application.generation.testgen.prompting.obligations_block_renderer import (
    ObligationsBlockRenderer,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.language.snake_case_converter import SnakeCaseConverter
from squeaky_clean.application.shared.mcda.per_module_criterion_filter import (
    filter_criteria_for_module,
)


class TestArchitectureContextFormatter:
    """Renders a TestArchitectureContext into the TestArchitect user prompt."""

    def __init__(self) -> None:
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._paths: ClassPathsBlockRenderer = ClassPathsBlockRenderer()
        self._obligations: ObligationsBlockRenderer = ObligationsBlockRenderer()

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
        lines.extend(self._obligations.render(ctx))
        classes = ClassLineRenderer(ctx)
        lines.append("Classes:")
        for cls in module.classes:
            lines.append(classes.class_line(cls, module))
        if layered and ctx.architecture is not None:
            extra = classes.cross_module(module, ctx.architecture)
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

    def _is_layered(self, ctx: TestArchitectureContext) -> bool:
        return (
            ctx.toolkit is not None
            and ctx.toolkit.identifier_case == "snake"
        )
