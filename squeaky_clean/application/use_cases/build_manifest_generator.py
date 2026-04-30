"""BuildManifestGenerator: emit a Maven pom.xml from resolved Java TechSpecs."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.build_manifest_helpers import (
    is_spring_technology,
    parse_install_package,
    render_dependency,
    render_test_dependency,
)
from squeaky_clean.application.use_cases.build_manifest_templates import (
    PARENT,
    PLAIN_BUILD,
    POM_TEMPLATE,
    SPRING_BUILD,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class BuildManifestGenerator:
    """Pure-function-style use case that writes ``pom.xml`` for Java projects."""

    def generate(
        self,
        architecture: ArchitectureSpec,
        tech_specs: dict[str, TechSpec],
        output_dir: Path,
        problem: ProblemSpec,
    ) -> Path | None:
        """Emit ``<output_dir>/pom.xml`` and return the path (or None if no Java)."""
        java_specs = [s for s in tech_specs.values() if s.language == "java"]
        if not java_specs:
            return None
        spring = any(is_spring_technology(s.technology) for s in java_specs)
        # Skip stdlib TechSpecs (JDK built-ins like java.nio.file). They
        # are already on the classpath and have no Maven coordinates.
        external = [
            s for s in java_specs
            if str(s.install.get("manager", "")) != "stdlib"
        ]
        deps = [
            render_dependency(*parse_install_package(
                str(s.install.get("package", "")),
            ))
            for s in external
        ]
        deps.append(render_test_dependency())
        body = self._render(problem.slug, spring, deps)
        path = output_dir / "pom.xml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    @staticmethod
    def _render(slug: str, spring: bool, deps: list[str]) -> str:
        parent = PARENT if spring else ""
        plugins = SPRING_BUILD if spring else PLAIN_BUILD
        return POM_TEMPLATE.format(
            slug=slug, parent=parent,
            dependencies="\n".join(deps), build=plugins,
        )
