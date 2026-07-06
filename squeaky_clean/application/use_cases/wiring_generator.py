"""WiringGenerator: emit a deterministic composition root (Python or Java).

Python target: ``src/main.py`` containing the wired ports/adapters/use-cases
plus a runtime block (Flask / Kafka loop / gRPC). Java target: a Spring Boot
``src/main/java/com/example/App.java`` whose component scanning + @Bean
configuration handles the wiring of @RestController / @KafkaListener / etc.
"""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.application.use_cases.wiring_construction import (
    emit_inbound,
    emit_outbound,
    emit_use_case,
)
from squeaky_clean.application.use_cases.wiring_templates import (
    render_express_main,
    render_fastify_main,
    render_go_main,
    render_runtime,
    render_rust_main,
    render_spring_boot_main,
)
from squeaky_clean.application.use_cases.wiring_walker import (
    adapters,
    first_with_category,
    split_inbound,
    use_cases,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class WiringGenerator:
    """Walks an ArchitectureSpec and emits a composition root file."""

    def __init__(self) -> None:
        self._snake: SnakeCaseConverter = SnakeCaseConverter()

    def generate(
        self, arch: ArchitectureSpec,
        tech_specs: dict[str, TechSpec],
        output_dir: Path,
    ) -> Path:
        """Write the composition root and return its path.

        Dispatches on TechSpec language: when ANY TechSpec declares
        ``language == "java"``, emit the Spring Boot ``App.java``;
        otherwise fall back to the Python ``src/main.py`` template.
        Python-specific assumptions (dotted import paths, snake_case
        var names) ONLY apply on the Python path.
        """
        if self._is_java(tech_specs):
            return self._emit_java(output_dir)
        if self._is_go(tech_specs):
            return self._emit_go(tech_specs, output_dir)
        if self._is_rust(tech_specs):
            return self._emit_rust(tech_specs, output_dir)
        if self._is_typescript(tech_specs):
            return self._emit_typescript(tech_specs, output_dir)
        if self._is_javascript(tech_specs):
            return self._emit_javascript(tech_specs, output_dir)
        adps = adapters(arch)
        ucs = use_cases(arch)
        body = self._render(adps, ucs, tech_specs)
        path = output_dir / "src" / "main.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    @staticmethod
    def _is_java(tech_specs: dict[str, TechSpec]) -> bool:
        return any(s.language == "java" for s in tech_specs.values())

    @staticmethod
    def _emit_java(output_dir: Path) -> Path:
        path = output_dir / "src" / "main" / "java" / "com" / "example" / "App.java"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_spring_boot_main())
        return path

    @staticmethod
    def _is_go(tech_specs: dict[str, TechSpec]) -> bool:
        return any(s.language == "go" for s in tech_specs.values())

    @staticmethod
    def _emit_go(tech_specs: dict[str, TechSpec], output_dir: Path) -> Path:
        path = output_dir / "main.go"
        path.parent.mkdir(parents=True, exist_ok=True)
        cats: dict[str, object] = {s.category: True for s in tech_specs.values()
                                   if s.language == "go"}
        path.write_text(render_go_main(cats))
        return path

    @staticmethod
    def _is_rust(tech_specs: dict[str, TechSpec]) -> bool:
        return any(s.language == "rust" for s in tech_specs.values())

    @staticmethod
    def _emit_rust(tech_specs: dict[str, TechSpec], output_dir: Path) -> Path:
        path = output_dir / "src" / "main.rs"
        path.parent.mkdir(parents=True, exist_ok=True)
        cats: dict[str, object] = {s.category: True for s in tech_specs.values()
                                   if s.language == "rust"}
        path.write_text(render_rust_main(cats))
        return path

    @staticmethod
    def _is_javascript(tech_specs: dict[str, TechSpec]) -> bool:
        return any(s.language == "javascript" for s in tech_specs.values())

    @staticmethod
    def _emit_javascript(tech_specs: dict[str, TechSpec],
                         output_dir: Path) -> Path:
        path = output_dir / "index.js"
        path.parent.mkdir(parents=True, exist_ok=True)
        cats: dict[str, object] = {s.category: True for s in tech_specs.values()
                                   if s.language == "javascript"}
        path.write_text(render_express_main(cats))
        return path

    @staticmethod
    def _is_typescript(tech_specs: dict[str, TechSpec]) -> bool:
        return any(s.language == "typescript" for s in tech_specs.values())

    @staticmethod
    def _emit_typescript(tech_specs: dict[str, TechSpec],
                         output_dir: Path) -> Path:
        path = output_dir / "src" / "index.ts"
        path.parent.mkdir(parents=True, exist_ok=True)
        # Carry the technology (not a bare True) so the renderer can match
        # the wiring's HTTP framework to the resolved handler (e.g. express).
        cats: dict[str, object] = {s.category: s.technology
                                   for s in tech_specs.values()
                                   if s.language == "typescript"}
        path.write_text(render_fastify_main(cats))
        return path

    def _render(
        self,
        adps: tuple[tuple[ModuleSpec, ClassSpec], ...],
        ucs: tuple[tuple[ModuleSpec, ClassSpec], ...],
        tech_specs: dict[str, TechSpec],
    ) -> str:
        out: list[str] = ['"""Auto-generated composition root (WiringGenerator)."""',
                          "from __future__ import annotations", "import os"]
        out.extend(self._import_for(m, c) for m, c in adps + ucs)
        out.append("")
        outbound, inbound = split_inbound(adps)
        sv: dict[str, str] = {}
        out.extend(emit_outbound(c, tech_specs, sv) for _m, c in outbound)
        out.extend(emit_use_case(c, sv) for _m, c in ucs)
        out.extend(emit_inbound(c, tech_specs, sv) for _m, c in inbound)
        out.append("")
        rest = first_with_category(adps, "rest_server_handler")
        kafka = first_with_category(adps, "message_queue_consumer")
        grpc = first_with_category(adps, "grpc_server_handler")
        out.append(render_runtime(
            sv[rest.name] if rest else None,
            sv[kafka.name] if kafka else None,
            sv[grpc.name] if grpc else None,
            next(iter(sv.values()), "use_case")))
        return "\n".join(out) + "\n"

    def _import_for(self, mod: ModuleSpec, cls: ClassSpec) -> str:
        layer = mod.layer.value.lower()
        return (f"from src.{layer}.{self._snake.convert(mod.name)}"
                f".{self._snake.convert(cls.name)} import {cls.name}")
