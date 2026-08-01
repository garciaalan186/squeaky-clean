"""ManifestEmitter: build-manifest + per-language dependency manifests."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.integration.manifests.build_manifest_generator import (  # noqa: E501
    BuildManifestGenerator,
)
from squeaky_clean.application.generation.integration.manifests.cargo_toml_generator import (  # noqa: E501
    generate_cargo_toml,
)
from squeaky_clean.application.generation.integration.manifests.go_mod_generator import (
    generate_go_mod,
)
from squeaky_clean.application.generation.integration.manifests.manifest_write_error import (  # noqa: E501
    ManifestWriteError,
)
from squeaky_clean.application.generation.integration.manifests.package_json_generator import (  # noqa: E501
    generate as generate_package_json,
)
from squeaky_clean.application.generation.integration.manifests.python_requirements_generator import (  # noqa: E501
    generate as generate_python_requirements,
)
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class ManifestEmitter:
    """Best-effort emission of build/dependency manifests, loudly logged."""

    def __init__(self, logger: RunLogger, fs: ProjectFileSystem) -> None:
        self._logger = logger
        self._fs = fs

    def emit(self, ctx: PipelineContext) -> None:
        arch, specs = ctx.arch, ctx.tech_specs
        assert arch is not None
        emitters: tuple[tuple[str, Callable[[], Path | None]], ...] = (
            ("build_manifest", lambda: BuildManifestGenerator(
                self._fs, ctx.problem).generate(specs, ctx.output_dir)),
            ("go_mod", lambda: generate_go_mod(
                arch, specs, ctx.output_dir, ctx.problem, fs=self._fs)),
            ("cargo_toml", lambda: generate_cargo_toml(
                arch, specs, ctx.output_dir, ctx.problem, fs=self._fs)),
        )
        for name, gen in emitters:
            try:
                path = gen()
                if path is not None:
                    self._logger.event(f"{name}_emitted", path=str(path))
            except (OSError, ManifestWriteError) as exc:
                self._logger.event(f"{name}_emit_failed", error=str(exc))
        self._emit_python_or_npm(ctx)

    def _emit_python_or_npm(self, ctx: PipelineContext) -> None:
        arch = ctx.arch
        assert arch is not None
        lang = ctx.problem.target_language
        try:
            if lang is TargetLanguage.PYTHON:
                path = generate_python_requirements(
                    arch, ctx.tech_specs, ctx.output_dir, ctx.problem,
                    fs=self._fs)
                if path is not None:
                    self._logger.event(
                        "requirements_txt_emitted", path=str(path))
            elif lang in (TargetLanguage.JAVASCRIPT, TargetLanguage.TYPESCRIPT):
                path = generate_package_json(
                    arch, ctx.tech_specs, ctx.output_dir, ctx.problem,
                    fs=self._fs)
                self._logger.event("package_json_emitted", path=str(path))
        except (OSError, ManifestWriteError) as exc:
            self._logger.event("manifest_emit_failed", error=str(exc))
