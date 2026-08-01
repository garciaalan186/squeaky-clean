"""Tests for tsconfig_generator: tsconfig.json emission for TS runs."""

import json
from pathlib import Path

import pytest

from squeaky_clean.application.generation.integration.manifests.manifest_write_error import (
    ManifestWriteError,
)
from squeaky_clean.application.generation.integration.manifests.tsconfig_generator import generate
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def _problem(lang: TargetLanguage = TargetLanguage.TYPESCRIPT) -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug="demo", description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(0, 1), expected_class_count=(0, 1),
        required_patterns=[], target_language=lang,
    )


def _ts_spec() -> TechSpec:
    return TechSpec(
        schema_version="v1", category="kv_cache", technology="t",
        version_pin="x", language="typescript",
        install={"manager": "npm", "package": "ioredis@^5.3.0"},
        imports={"primary": "import x"},
        client_construction={"code": "x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_tsconfig_emitted_for_typescript_problem(tmp_path: Path) -> None:
    out = generate({}, tmp_path, _problem(TargetLanguage.TYPESCRIPT), fs=LocalFileSystem())
    assert out == tmp_path / "tsconfig.json"
    body = json.loads(out.read_text())
    assert body["compilerOptions"]["strict"] is True
    assert body["compilerOptions"]["target"] == "ES2022"
    assert body["compilerOptions"]["esModuleInterop"] is True


def test_tsconfig_skipped_for_non_typescript(tmp_path: Path) -> None:
    out = generate({}, tmp_path, _problem(TargetLanguage.PYTHON), fs=LocalFileSystem())
    assert out is None


def test_tsconfig_emitted_when_any_techspec_typescript(tmp_path: Path) -> None:
    out = generate({"x": _ts_spec()}, tmp_path,
                   _problem(TargetLanguage.PYTHON), fs=LocalFileSystem())
    assert out is not None
    body = json.loads(out.read_text())
    assert body["compilerOptions"]["strict"] is True


class _FailingFs(ProjectFileSystem):
    def read(self, path: Path) -> str:
        raise OSError("read-only")

    def write(self, path: Path, content: str) -> None:
        raise OSError("disk full")

    def list_files(self, root: Path) -> list[Path]:
        return []


def test_write_failure_raises_manifest_write_error(tmp_path: Path) -> None:
    """R6.8: OSError is translated into ManifestWriteError, never a None."""
    with pytest.raises(ManifestWriteError, match="disk full"):
        generate({}, tmp_path, _problem(TargetLanguage.TYPESCRIPT), fs=_FailingFs())
