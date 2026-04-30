"""Tests for python_requirements_generator: requirements.txt emission."""

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.python_requirements_generator import generate
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
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def _spec(category: str, package: str, manager: str = "pip",
          language: str = "python") -> TechSpec:
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


def test_returns_none_when_no_python_specs(tmp_path: Path) -> None:
    java = _spec("rest_server_handler", "junit:junit:4.13",
                 manager="maven", language="java")
    out = generate(_arch(), {"x": java}, tmp_path, _problem())
    assert out is None
    assert not (tmp_path / "requirements.txt").exists()


def test_emits_one_line_per_pip_spec(tmp_path: Path) -> None:
    spec = _spec("message_queue_consumer", "confluent-kafka==2.5")
    out = generate(_arch(), {"mq": spec}, tmp_path, _problem())
    assert out == tmp_path / "requirements.txt"
    body = out.read_text()
    assert body.strip() == "confluent-kafka==2.5"


def test_emits_multiple_specs(tmp_path: Path) -> None:
    a = _spec("message_queue_consumer", "confluent-kafka==2.5")
    b = _spec("blob_storage", "boto3==1.34")
    out = generate(_arch(), {"mq": a, "blob": b}, tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert "confluent-kafka==2.5" in body
    assert "boto3==1.34" in body


def test_skips_stdlib_specs(tmp_path: Path) -> None:
    stdlib = _spec("blob_storage", "stdlib", manager="stdlib")
    pip = _spec("message_queue_consumer", "confluent-kafka==2.5")
    out = generate(_arch(), {"a": stdlib, "b": pip}, tmp_path, _problem())
    assert out is not None
    body = out.read_text()
    assert "stdlib" not in body
    assert "confluent-kafka==2.5" in body
