"""validate_http_conventions: enforce constraint #22 HTTP type conventions.

Pure function over an in-memory ``ArchitectureSpec``. Returns one
human-readable violation string per HTTP-shape parameter whose declared
§Notation type does not match the canonical HTTP convention type.
"""

from __future__ import annotations

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.http_method_signature_parser import parse_method
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec

_HTTP_CATEGORIES: frozenset[str] = frozenset({
    "rest_server_handler", "rest_client",
    "grpc_server_handler", "grpc_client",
    "websocket_server_handler",
})
_HTTP_PATTERNS: frozenset[str] = frozenset({"Adapter", "Gateway", "Repository"})
_DICT_OK: frozenset[str] = frozenset({
    "dict[str, str]", "dict[str,str]", "Map<String, String>",
    "Map<String,String>", "dict",
})
_BODY_OK: frozenset[str] = frozenset({"bytes", "str"})
_QUERY_NAMES: frozenset[str] = frozenset({"query", "query_params", "queryParams"})
_STATUS_NAMES: frozenset[str] = frozenset({"status_code", "statusCode"})


def validate_http_conventions(
    arch: ArchitectureSpec, problem: ProblemSpec,
) -> tuple[str, ...]:
    """Return violations of constraint #22 — HTTP headers/body/query/status types."""
    if not any(c.category in _HTTP_CATEGORIES
               for c in problem.infrastructure_choices):
        return ()
    out: list[str] = []
    for module in arch.modules:
        for cls in module.classes:
            if cls.pattern not in _HTTP_PATTERNS:
                continue
            for method in cls.methods:
                out.extend(_check_method(module.name, cls, method))
    return tuple(out)


def _check_method(
    module_name: str, cls: ClassSpec, method: str,
) -> list[str]:
    name, args, ret = parse_method(method)
    out: list[str] = []
    for arg_name, arg_type in args:
        expected = _check_param(arg_name, arg_type)
        if expected is not None:
            out.append(_fmt(module_name, cls.name, name, arg_name,
                            arg_type, expected))
    if name in _STATUS_NAMES and ret and ret != "int":
        out.append(_fmt(module_name, cls.name, name, "<return>", ret, "int"))
    return out


def _check_param(arg_name: str, arg_type: str) -> str | None:
    low = arg_name.lower()
    if low == "headers" and arg_type not in _DICT_OK:
        return "dict[str, str]"
    if low == "body" and arg_type not in _BODY_OK:
        return "bytes or str"
    if arg_name in _QUERY_NAMES and arg_type not in _DICT_OK:
        return "dict[str, str]"
    return None


def _fmt(
    mod: str, cls: str, meth: str, param: str, declared: str, expected: str,
) -> str:
    return (f"module {mod!r} class {cls!r} method {meth!r} "
            f"parameter {param!r}: declared {declared!r}, "
            f"expected {expected!r} (constraint #22)")
