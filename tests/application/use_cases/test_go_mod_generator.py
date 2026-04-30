"""Tests for go_mod_generator: go.mod emission for Go projects."""

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.go_mod_generator import generate_go_mod
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
        required_patterns=[], target_language=TargetLanguage.GO,
    )


def _spec(category: str, technology: str, package: str,
          language: str = "go") -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology=technology,
        version_pin="x", language=language,
        install={"manager": "go", "package": package},
        imports={"primary": "x"},
        client_construction={"code": "x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_returns_none_when_no_go_tech_specs(tmp_path: Path) -> None:
    py = _spec("rest_server_handler", "fastapi",
               "fastapi==0.110", language="python")
    out = generate_go_mod(_arch(), {"rest_server_handler": py},
                         tmp_path, _problem())
    assert out is None
    assert not (tmp_path / "go.mod").exists()


def test_writes_go_mod_with_aws_s3_dependency(tmp_path: Path) -> None:
    spec = _spec("blob_storage", "aws_s3_go",
                 "github.com/aws/aws-sdk-go-v2/service/s3@v1.66.0")
    out = generate_go_mod(_arch(), {"blob_storage": spec},
                         tmp_path, _problem("svc"))
    assert out == tmp_path / "go.mod"
    body = out.read_text()
    assert "module com.example/svc" in body
    assert "go 1.21" in body
    assert "github.com/aws/aws-sdk-go-v2/service/s3 v1.66.0" in body
    assert "require (" in body


def test_writes_go_mod_with_redis_dependency(tmp_path: Path) -> None:
    spec = _spec("kv_cache", "go_redis",
                 "github.com/redis/go-redis/v9@v9.5.0")
    out = generate_go_mod(_arch(), {"kv_cache": spec}, tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert "github.com/redis/go-redis/v9 v9.5.0" in body


def test_skips_stdlib_packages(tmp_path: Path) -> None:
    spec = _spec("blob_storage", "local_disk", "stdlib")
    out = generate_go_mod(_arch(), {"blob_storage": spec},
                         tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert "module com.example/" in body
    assert "require (" not in body


def test_dedupes_duplicate_packages(tmp_path: Path) -> None:
    a = _spec("message_queue_producer", "sarama",
              "github.com/IBM/sarama@v1.42.1")
    b = _spec("message_queue_consumer", "sarama",
              "github.com/IBM/sarama@v1.42.1")
    out = generate_go_mod(_arch(), {"p": a, "c": b},
                         tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert body.count("github.com/IBM/sarama") == 1
