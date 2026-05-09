"""Unit tests for validate_http_conventions (constraint #22)."""

from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.validate_http_conventions import (
    validate_http_conventions,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _problem(*choices: tuple[str, str]) -> ProblemSpec:
    return ProblemSpec(
        id="X", tier=0, slug="x", description="d",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
        infrastructure_choices=tuple(
            InfrastructureChoice(category=c, technology=t, version_pin="1.0")
            for c, t in choices
        ),
    )


def _arch(cls: ClassSpec, *, name: str = "M") -> ArchitectureSpec:
    mod = ModuleSpec(
        name=name, layer=LayerType.INFRASTRUCTURE, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def _adapter(*methods: str) -> ClassSpec:
    return ClassSpec(
        name="EventController", pattern="Adapter", implements=None,
        methods=tuple(methods), depends=(), concretes=(),
    )


def test_clean_python_dict_str_str_no_violations() -> None:
    cls = _adapter("handle(headers: dict[str, str]): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "fastapi")))
    assert out == ()


def test_java_string_array_headers_flagged() -> None:
    cls = _adapter("handle(headers: String[]): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert len(out) == 1
    assert "headers" in out[0]
    assert "String[]" in out[0]
    assert "dict[str, str]" in out[0]
    assert "constraint #22" in out[0]


def test_java_map_string_string_accepted() -> None:
    cls = _adapter("handle(headers: Map<String, String>): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert out == ()


def test_no_http_infrastructure_no_checks() -> None:
    cls = _adapter("handle(headers: String[]): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("relational_db", "postgres")))
    assert out == ()


def test_multi_violation_headers_and_body() -> None:
    cls = _adapter("handle(headers: String[], body: int): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert len(out) == 2
    assert any("headers" in v for v in out)
    assert any("body" in v for v in out)


def test_query_param_string_array_flagged() -> None:
    cls = _adapter("handle(query: String[]): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert len(out) == 1
    assert "query" in out[0]


def test_status_code_return_type_string_flagged() -> None:
    cls = _adapter("status_code(): String")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert len(out) == 1
    assert "<return>" in out[0]
    assert "'int'" in out[0]


def test_empty_architecture_no_violations() -> None:
    arch = ArchitectureSpec(modules=(), graph=ArchitectureGraph(edges={}))
    out = validate_http_conventions(
        arch, _problem(("rest_server_handler", "spring_boot")))
    assert out == ()


def test_non_http_pattern_skipped() -> None:
    cls = ClassSpec(
        name="EventEntity", pattern="Entity", implements=None,
        methods=("handle(headers: String[]): int",), depends=(), concretes=(),
    )
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "spring_boot")))
    assert out == ()


def test_grpc_server_triggers_check() -> None:
    cls = _adapter("call(headers: String[]): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("grpc_server_handler", "grpc_java")))
    assert len(out) == 1


def test_body_str_accepted() -> None:
    cls = _adapter("handle(body: str): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "fastapi")))
    assert out == ()


def test_body_bytes_accepted() -> None:
    cls = _adapter("handle(body: bytes): int")
    out = validate_http_conventions(
        _arch(cls), _problem(("rest_server_handler", "fastapi")))
    assert out == ()
