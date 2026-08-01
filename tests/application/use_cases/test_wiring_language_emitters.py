"""Tests for WiringLanguageEmitters (extracted from WiringGenerator)."""

from pathlib import Path

from squeaky_clean.application.generation.integration.wiring_language_emitters import (
    WiringLanguageEmitters,
)
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def _tech_spec(category: str, language: str) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="express",
        version_pin="v1", language=language,
        install={"manager": "npm", "package": "x"},
        imports={"primary": "import x"},
        client_construction={"code": "self._x = x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="() -> None", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_python_only_specs_yield_none(tmp_path: Path) -> None:
    specs = {"rest_server_handler": _tech_spec("rest_server_handler", "python")}
    emitters = WiringLanguageEmitters(LocalFileSystem())
    assert emitters.emit(specs, tmp_path) is None


def test_java_spec_emits_spring_boot_app(tmp_path: Path) -> None:
    specs = {"rest_server_handler": _tech_spec("rest_server_handler", "java")}
    path = WiringLanguageEmitters(LocalFileSystem()).emit(specs, tmp_path)
    assert path == (tmp_path / "src" / "main" / "java" / "com"
                    / "example" / "App.java")
    assert "class App" in path.read_text()


def test_go_spec_emits_main_go(tmp_path: Path) -> None:
    specs = {"rest_server_handler": _tech_spec("rest_server_handler", "go")}
    path = WiringLanguageEmitters(LocalFileSystem()).emit(specs, tmp_path)
    assert path == tmp_path / "main.go"
    assert "package main" in path.read_text()


def test_typescript_spec_emits_index_ts_with_technology_cats(
    tmp_path: Path,
) -> None:
    specs = {
        "rest_server_handler": _tech_spec("rest_server_handler", "typescript"),
    }
    path = WiringLanguageEmitters(LocalFileSystem()).emit(specs, tmp_path)
    assert path == tmp_path / "src" / "index.ts"
    assert path.read_text().strip() != ""
