"""Tests for cargo_toml_generator: Cargo.toml emission for Rust projects."""

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.cargo_toml_generator import generate_cargo_toml
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _arch() -> ArchitectureSpec:
    return ArchitectureSpec(modules=(), graph=ArchitectureGraph(edges={}))


def _problem(slug: str = "demo_app") -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug=slug, description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(0, 1), expected_class_count=(0, 1),
        required_patterns=[], target_language=TargetLanguage.RUST,
    )


def _spec(category: str, technology: str, package: str,
          language: str = "rust", manager: str = "cargo") -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology=technology,
        version_pin="x", language=language,
        install={"manager": manager, "package": package},
        imports={"primary": "use x;"},
        client_construction={"code": "let _ = ();", "is_async": True,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_returns_none_when_no_rust_tech_specs(tmp_path: Path) -> None:
    py = _spec("rest_server_handler", "fastapi",
               "fastapi==0.110", language="python", manager="pip")
    out = generate_cargo_toml(_arch(), {"rest_server_handler": py},
                              tmp_path, _problem())
    assert out is None
    assert not (tmp_path / "Cargo.toml").exists()


def test_writes_cargo_toml_with_aws_s3_dependency(tmp_path: Path) -> None:
    spec = _spec("blob_storage", "aws_s3_rust", "aws-sdk-s3==1.40")
    out = generate_cargo_toml(_arch(), {"blob_storage": spec},
                              tmp_path, _problem("svc"))
    assert out == tmp_path / "Cargo.toml"
    body = out.read_text()
    assert 'name = "svc"' in body
    assert 'edition = "2021"' in body
    assert 'tokio = { version = "1.36", features = ["full"] }' in body
    assert 'aws-sdk-s3 = "1.40"' in body


def test_writes_cargo_toml_with_redis_dependency(tmp_path: Path) -> None:
    spec = _spec("kv_cache", "redis_rust", "redis==0.25")
    out = generate_cargo_toml(_arch(), {"kv_cache": spec},
                              tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert 'redis = "0.25"' in body
    assert "tokio = " in body


def test_skips_stdlib_packages(tmp_path: Path) -> None:
    spec = _spec("blob_storage", "local_disk", "stdlib", manager="stdlib")
    out = generate_cargo_toml(_arch(), {"blob_storage": spec},
                              tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert "tokio = " in body  # always present
    # only tokio in deps section, no stdlib entry
    assert "stdlib" not in body


def test_dedupes_duplicate_packages(tmp_path: Path) -> None:
    a = _spec("message_queue_producer", "rdkafka", "rdkafka==0.36")
    b = _spec("message_queue_consumer", "rdkafka", "rdkafka==0.36")
    out = generate_cargo_toml(_arch(), {"p": a, "c": b},
                              tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert body.count("rdkafka =") == 1
