"""Tests for BuildManifestGenerator: pom.xml emission for Java projects."""

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.build_manifest_generator import (
    BuildManifestGenerator,
)
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
        required_patterns=[], target_language=TargetLanguage.JAVA,
    )


def _spec(category: str, technology: str, package: str,
          language: str = "java") -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology=technology,
        version_pin="x", language=language,
        install={"manager": "maven", "package": package},
        imports={"primary": "import x;"},
        client_construction={"code": "x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_returns_none_when_no_java_tech_specs(tmp_path: Path) -> None:
    py_spec = _spec("rest_server_handler", "fastapi", "fastapi==0.110",
                    language="python")
    result = BuildManifestGenerator().generate(
        _arch(), {"rest_server_handler": py_spec}, tmp_path, _problem(),
    )
    assert result is None
    assert not (tmp_path / "pom.xml").exists()


def test_writes_pom_for_spring_boot_with_parent(tmp_path: Path) -> None:
    rest = _spec("rest_server_handler", "spring_boot",
                 "org.springframework.boot:spring-boot-starter-web:3.2.0")
    path = BuildManifestGenerator().generate(
        _arch(), {"rest_server_handler": rest}, tmp_path, _problem("svc"),
    )
    assert path == tmp_path / "pom.xml"
    body = path.read_text()
    assert "<artifactId>svc</artifactId>" in body
    assert "<artifactId>spring-boot-starter-parent</artifactId>" in body
    assert "spring-boot-maven-plugin" in body
    assert "<artifactId>spring-boot-starter-web</artifactId>" in body
    assert "<artifactId>junit-jupiter</artifactId>" in body
    assert "<java.version>11</java.version>" in body


def test_writes_pom_with_kafka_dependency(tmp_path: Path) -> None:
    kp = _spec("message_queue_producer", "spring_kafka",
               "spring-kafka==3.1")
    path = BuildManifestGenerator().generate(
        _arch(), {"mq": kp}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "<groupId>org.springframework.kafka</groupId>" in body
    assert "<artifactId>spring-kafka</artifactId>" in body
    assert "<version>3.1</version>" in body


def test_writes_pom_without_parent_for_non_spring(tmp_path: Path) -> None:
    other = _spec("blob_storage", "local_disk", "junit:junit:4.13")
    path = BuildManifestGenerator().generate(
        _arch(), {"blob": other}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "spring-boot-starter-parent" not in body
    assert "spring-boot-maven-plugin" not in body
    assert "maven-surefire-plugin" in body


def test_j1_writes_spring_data_jdbc_dependency(tmp_path: Path) -> None:
    db = _spec("relational_db", "spring_data_jdbc",
               "spring-boot-starter-data-jdbc==2.7")
    path = BuildManifestGenerator().generate(
        _arch(), {"db": db}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "<groupId>org.springframework.boot</groupId>" in body
    assert "<artifactId>spring-boot-starter-data-jdbc</artifactId>" in body
    assert "<version>2.7</version>" in body
    assert "<artifactId>spring-boot-starter-parent</artifactId>" in body


def test_j1_writes_lettuce_redis_dependency(tmp_path: Path) -> None:
    cache = _spec("kv_cache", "lettuce", "lettuce-core==6.3")
    path = BuildManifestGenerator().generate(
        _arch(), {"cache": cache}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "<groupId>io.lettuce</groupId>" in body
    assert "<artifactId>lettuce-core</artifactId>" in body
    assert "<version>6.3</version>" in body


def test_j1_writes_grpc_netty_dependency(tmp_path: Path) -> None:
    rpc = _spec("grpc_client", "grpc_java", "grpc-netty-shaded==1.62")
    path = BuildManifestGenerator().generate(
        _arch(), {"rpc": rpc}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "<groupId>io.grpc</groupId>" in body
    assert "<artifactId>grpc-netty-shaded</artifactId>" in body
    assert "<version>1.62</version>" in body


def test_j1_writes_kafka_streams_dependency(tmp_path: Path) -> None:
    stream = _spec("stream_processor", "kafka_streams", "kafka-streams==3.6")
    path = BuildManifestGenerator().generate(
        _arch(), {"stream": stream}, tmp_path, _problem(),
    )
    assert path is not None
    body = path.read_text()
    assert "<groupId>org.apache.kafka</groupId>" in body
    assert "<artifactId>kafka-streams</artifactId>" in body
    assert "<version>3.6</version>" in body
