"""BuildManifestGenerator: emit a Maven pom.xml from resolved Java TechSpecs."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.generation.integration.manifests.build_manifest_helpers import (
    is_spring_technology,
    parse_install_package,
    render_dependency,
    render_managed_dependency,
    render_test_dependency,
)
from squeaky_clean.application.generation.integration.manifests.build_manifest_templates import (
    PARENT,
    PLAIN_BUILD,
    POM_TEMPLATE,
    SPRING_BUILD,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


class BuildManifestGenerator:
    """Writes ``pom.xml`` for Java projects via the ProjectFileSystem port."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def generate(
        self,
        architecture: ArchitectureSpec,
        tech_specs: dict[str, TechSpec],
        output_dir: Path,
        problem: ProblemSpec,
    ) -> Path | None:
        """Emit ``<output_dir>/pom.xml``; None ONLY when not applicable (no Java).

        Write errors are never swallowed here: ``fs.write`` OSErrors
        propagate to ManifestEmitter, which logs the failure event (R6.8).
        """
        java_specs = [s for s in tech_specs.values() if s.language == "java"]
        if not java_specs:
            return None
        spring = any(is_spring_technology(s.technology) for s in java_specs)
        # Skip stdlib TechSpecs (JDK built-ins): no Maven coordinates.
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
        # Spring apps need the base starter + Jackson explicitly: a web app
        # gets both transitively from spring-boot-starter-web, but a pure
        # consumer/worker has no web starter (parent-managed; no-op if web).
        if spring:
            deps.append(render_managed_dependency(
                "org.springframework.boot", "spring-boot-starter"))
            deps.append(render_managed_dependency(
                "com.fasterxml.jackson.core", "jackson-databind"))
        deps.append(render_test_dependency())
        body = self._render(problem.slug, spring, deps)
        path = output_dir / "pom.xml"
        self._fs.write(path, body)
        return path

    @staticmethod
    def _render(slug: str, spring: bool, deps: list[str]) -> str:
        parent = PARENT if spring else ""
        plugins = SPRING_BUILD if spring else PLAIN_BUILD
        return POM_TEMPLATE.format(
            slug=slug, parent=parent,
            dependencies="\n".join(deps), build=plugins,
        )
