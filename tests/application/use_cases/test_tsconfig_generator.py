"""Tests for tsconfig_generator: tsconfig.json emission for TS runs."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.tsconfig_generator import generate
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


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
    out = generate({}, tmp_path, _problem(TargetLanguage.TYPESCRIPT))
    assert out == tmp_path / "tsconfig.json"
    body = json.loads(out.read_text())
    assert body["compilerOptions"]["strict"] is True
    assert body["compilerOptions"]["target"] == "ES2022"
    assert body["compilerOptions"]["esModuleInterop"] is True


def test_tsconfig_skipped_for_non_typescript(tmp_path: Path) -> None:
    out = generate({}, tmp_path, _problem(TargetLanguage.PYTHON))
    assert out is None


def test_tsconfig_emitted_when_any_techspec_typescript(tmp_path: Path) -> None:
    out = generate({"x": _ts_spec()}, tmp_path,
                   _problem(TargetLanguage.PYTHON))
    assert out is not None
    body = json.loads(out.read_text())
    assert body["compilerOptions"]["strict"] is True
