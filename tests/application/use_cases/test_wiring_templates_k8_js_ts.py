"""Tests for K8 JS/TS composition-root templates and dispatch."""

from pathlib import Path

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.wiring_generator import WiringGenerator
from squeaky_clean.application.use_cases.wiring_templates import (
    render_express_main,
    render_fastify_main,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _spec(category: str, language: str) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="t",
        version_pin="x", language=language,
        install={"manager": "npm", "package": "x@^1.0.0"},
        imports={"primary": "import x"},
        client_construction={"code": "x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def _arch() -> ArchitectureSpec:
    cls = ClassSpec(name="Stub", pattern="SimpleClass",
                    implements=None, methods=(), depends=(), concretes=())
    mod = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(cls,), invariants=())
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def test_render_express_main_for_rest() -> None:
    body = render_express_main({"rest_server_handler": True})
    assert "require('express')" in body
    assert "app.listen(" in body


def test_render_express_main_for_consumer() -> None:
    body = render_express_main({"message_queue_consumer": True})
    assert "consumer started" in body
    assert "setInterval" in body


def test_render_express_main_default() -> None:
    body = render_express_main({})
    assert "service ready" in body


def test_render_fastify_main_for_rest() -> None:
    body = render_fastify_main({"rest_server_handler": True})
    assert "import Fastify" in body
    assert "app.listen(" in body


def test_render_fastify_main_for_consumer() -> None:
    body = render_fastify_main({"message_queue_consumer": True})
    assert "consumer started" in body


def test_render_fastify_main_default() -> None:
    body = render_fastify_main({})
    assert "service ready" in body


def test_wiring_dispatches_javascript_to_index_js(tmp_path: Path) -> None:
    arch = _arch()
    specs = {"rest_server_handler":
             _spec("rest_server_handler", "javascript")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "index.js"
    body = path.read_text()
    assert "express" in body
    assert "app.listen" in body


def test_wiring_dispatches_typescript_to_src_index_ts(tmp_path: Path) -> None:
    arch = _arch()
    specs = {"rest_server_handler":
             _spec("rest_server_handler", "typescript")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "src" / "index.ts"
    body = path.read_text()
    assert "Fastify" in body
    assert "app.listen" in body


def test_wiring_typescript_takes_precedence_over_javascript(
    tmp_path: Path,
) -> None:
    arch = _arch()
    specs = {
        "rest_server_handler": _spec("rest_server_handler", "typescript"),
        "kv_cache": _spec("kv_cache", "javascript"),
    }
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "src" / "index.ts"
