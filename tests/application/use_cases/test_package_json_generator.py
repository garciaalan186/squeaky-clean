"""Tests for package_json_generator: package.json emission."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.package_json_generator import generate
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _arch() -> ArchitectureSpec:
    return ArchitectureSpec(modules=(), graph=ArchitectureGraph(edges={}))


def _problem(slug: str = "demo") -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug=slug, description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(0, 1), expected_class_count=(0, 1),
        required_patterns=[], target_language=TargetLanguage.JAVASCRIPT,
    )


def _spec(category: str, package: str,
          language: str = "javascript", manager: str = "npm") -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="t",
        version_pin="x", language=language,
        install={"manager": manager, "package": package},
        imports={"primary": "x"},
        client_construction={"code": "x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_emits_empty_package_json_when_no_js_specs(tmp_path: Path) -> None:
    out = generate(_arch(), {}, tmp_path, _problem("svc"))
    assert out == tmp_path / "package.json"
    body = json.loads(out.read_text())
    assert body["name"] == "svc"
    assert body["version"] == "1.0.0"
    assert body["dependencies"] == {}
    assert body["devDependencies"] == {"jest": "^29.7.0"}


def test_emits_one_dep_for_js_spec(tmp_path: Path) -> None:
    spec = _spec("kv_cache", "redis@4.6.0")
    out = generate(_arch(), {"cache": spec}, tmp_path, _problem("app"))
    assert out is not None
    body = json.loads(out.read_text())
    assert body["dependencies"] == {"redis": "4.6.0"}
    assert body["name"] == "app"
    assert "jest" in body["devDependencies"]


def test_emits_ts_dev_deps_for_typescript_spec(tmp_path: Path) -> None:
    spec = _spec("kv_cache", "ioredis@^5.3.0", language="typescript")
    out = generate(_arch(), {"cache": spec}, tmp_path, _problem("ts_app"))
    assert out is not None
    body = json.loads(out.read_text())
    assert "typescript" in body["devDependencies"]
    assert "ts-jest" in body["devDependencies"]
    assert "@types/node" in body["devDependencies"]
    assert "jest" in body["devDependencies"]
    assert body["dependencies"] == {"ioredis": "^5.3.0"}


def test_aggregates_unique_deps_across_specs(tmp_path: Path) -> None:
    a = _spec("kv_cache", "ioredis@^5.3.0")
    b = _spec("rest_client", "axios@^1.6.0")
    out = generate(_arch(), {"a": a, "b": b}, tmp_path, _problem("agg"))
    assert out is not None
    body = json.loads(out.read_text())
    assert body["dependencies"] == {"ioredis": "^5.3.0", "axios": "^1.6.0"}
