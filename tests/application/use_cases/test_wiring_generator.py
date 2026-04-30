"""Tests for WiringGenerator: composition root emission across runtime shapes."""

import ast
from pathlib import Path

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.wiring_generator import WiringGenerator
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _adapter(name: str, methods: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(name=name, pattern="Adapter", implements=None,
                     methods=methods, depends=(), concretes=())


def _use_case(name: str, depends: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(name=name, pattern="UseCase", implements=None,
                     methods=("execute(payload: dict): dict",),
                     depends=depends, concretes=())


def _arch(adapter_classes: tuple[ClassSpec, ...],
          use_case_classes: tuple[ClassSpec, ...]) -> ArchitectureSpec:
    mods: list[ModuleSpec] = []
    if adapter_classes:
        mods.append(ModuleSpec(
            name="InfraMod", layer=LayerType.INFRASTRUCTURE,
            exports=tuple(c.name for c in adapter_classes), depends=(),
            classes=adapter_classes, invariants=()))
    if use_case_classes:
        mods.append(ModuleSpec(
            name="AppMod", layer=LayerType.APPLICATION,
            exports=tuple(c.name for c in use_case_classes), depends=(),
            classes=use_case_classes, invariants=()))
    if not mods:
        mods.append(ModuleSpec(
            name="Empty", layer=LayerType.DOMAIN, exports=(), depends=(),
            classes=(ClassSpec(name="Stub", pattern="SimpleClass",
                               implements=None, methods=(), depends=(),
                               concretes=()),),
            invariants=()))
    return ArchitectureSpec(modules=tuple(mods),
                            graph=ArchitectureGraph(edges={}))


def _tech_spec(category: str, deps: list[str]) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="t",
        version_pin="v1", language="python",
        install={"manager": "pip", "package": "x"},
        imports={"primary": "import x"},
        client_construction={"code": "self._x = x", "is_async": False,
                             "thread_safe": True, "dependencies": deps},
        primary_operations=(TechSpecOperation(
            name="op", signature="() -> None", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_flask_runtime_with_kafka_producer(tmp_path: Path) -> None:
    rest = _adapter("FlaskHandler", ("handle(payload: dict): dict",))
    producer = _adapter("KafkaProducer",
                        ("publish(topic: str, payload: bytes): None",))
    arch = _arch((rest, producer), ())
    specs = {"rest_server_handler": _tech_spec("rest_server_handler",
                                               ["use_case"]),
             "message_queue_producer": _tech_spec("message_queue_producer",
                                                  ["bootstrap_servers"])}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    body = path.read_text()
    ast.parse(body)
    assert "Flask(__name__)" in body
    assert 'app.add_url_rule("/"' in body
    assert "KafkaProducer(" in body


def test_kafka_consumer_loop(tmp_path: Path) -> None:
    blob = _adapter("LocalDiskBlob",
                    ("put_blob(key: str, body: bytes): None",))
    consumer = _adapter("KafkaConsumer",
                        ("poll_one(timeout: float): bytes",))
    use_case = _use_case("ArchiveEvent", ("LocalDiskBlob",))
    arch = _arch((blob, consumer), (use_case,))
    specs = {
        "blob_storage": _tech_spec("blob_storage", ["root_dir"]),
        "message_queue_consumer": _tech_spec(
            "message_queue_consumer",
            ["KAFKA_BOOTSTRAP_SERVERS", "KAFKA_GROUP_ID", "KAFKA_TOPIC"]),
    }
    body = WiringGenerator().generate(arch, specs, tmp_path).read_text()
    ast.parse(body)
    assert "while True:" in body
    assert "KeyboardInterrupt" in body
    assert 'os.environ.get("KAFKA_BOOTSTRAP_SERVERS"' in body


def test_default_skeleton_when_no_inbound(tmp_path: Path) -> None:
    arch = _arch((), ())
    body = WiringGenerator().generate(arch, {}, tmp_path).read_text()
    ast.parse(body)
    assert "TODO: no inbound entry point" in body
    assert 'if __name__ == "__main__":' in body


def test_techspec_dependencies_become_environ_lookups(tmp_path: Path) -> None:
    blob = _adapter("LocalDiskBlobStore",
                    ("put_blob(key: str, body: bytes): None",))
    arch = _arch((blob,), ())
    specs = {"blob_storage": _tech_spec("blob_storage", ["root_dir"])}
    body = WiringGenerator().generate(arch, specs, tmp_path).read_text()
    ast.parse(body)
    assert 'os.environ.get("ROOT_DIR"' in body


def test_multiple_adapters_get_distinct_names(tmp_path: Path) -> None:
    a = _adapter("BlobStoreOne", ("put_blob(key: str, body: bytes): None",))
    b = _adapter("KafkaProducer",
                 ("publish(topic: str, payload: bytes): None",))
    arch = _arch((a, b), ())
    specs = {"blob_storage": _tech_spec("blob_storage", ["root_dir"]),
             "message_queue_producer": _tech_spec("message_queue_producer",
                                                  ["bootstrap_servers"])}
    body = WiringGenerator().generate(arch, specs, tmp_path).read_text()
    ast.parse(body)
    assert "blob_store_one =" in body
    assert "kafka_producer =" in body


def test_emitted_file_within_120_lines(tmp_path: Path) -> None:
    rest = _adapter("FlaskHandler", ("handle(payload: dict): dict",))
    use_case = _use_case("Ingest", ("FlaskHandler",))
    arch = _arch((rest,), (use_case,))
    specs = {"rest_server_handler": _tech_spec("rest_server_handler",
                                               ["use_case"])}
    body = WiringGenerator().generate(arch, specs, tmp_path).read_text()
    assert body.count("\n") <= 120


def _java_tech_spec(category: str) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="spring_boot",
        version_pin="v1", language="java",
        install={"manager": "maven", "package": "x"},
        imports={"primary": "import x;"},
        client_construction={"code": "this.x = x;", "is_async": False,
                             "thread_safe": True, "dependencies": ["use_case"]},
        primary_operations=(TechSpecOperation(
            name="op", signature="() -> None", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def _go_tech_spec(category: str) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="go_t",
        version_pin="v1", language="go",
        install={"manager": "go", "package": "example.com/x@v1"},
        imports={"primary": "\"x\""},
        client_construction={"code": "x := 1; _ = x", "is_async": False,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="() -> None", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_go_emits_main_go_for_rest(tmp_path: Path) -> None:
    rest = _adapter("StdlibIngest", ("Handle()",))
    arch = _arch((rest,), ())
    specs = {"rest_server_handler": _go_tech_spec("rest_server_handler")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "main.go"
    body = path.read_text()
    assert "package main" in body
    assert "import (" in body
    assert "\"net/http\"" in body
    assert "func main()" in body
    assert "http.ListenAndServe" in body


def test_go_emits_main_go_for_consumer(tmp_path: Path) -> None:
    consumer = _adapter("SaramaConsumer", ("ConsumeRaw()",))
    arch = _arch((consumer,), ())
    specs = {"message_queue_consumer": _go_tech_spec("message_queue_consumer")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    body = path.read_text()
    assert "package main" in body
    assert "signal.Notify" in body
    assert "syscall.SIGTERM" in body


def test_go_emits_default_skeleton_main_go(tmp_path: Path) -> None:
    blob = _adapter("LocalBlob", ("PutBlob()",))
    arch = _arch((blob,), ())
    specs = {"blob_storage": _go_tech_spec("blob_storage")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    body = path.read_text()
    assert "package main" in body
    assert "service ready" in body


def _rust_tech_spec(category: str) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="rust_t",
        version_pin="v1", language="rust",
        install={"manager": "cargo", "package": "x==1.0"},
        imports={"primary": "use x;"},
        client_construction={"code": "let _ = ();", "is_async": True,
                             "thread_safe": True, "dependencies": []},
        primary_operations=(TechSpecOperation(
            name="op", signature="() -> None", sdk_call="x",
            error_types=("E",), idempotency="idempotent",
            retry_policy="none"),),
        auth={"method": "none"})


def test_rust_emits_main_rs_for_rest(tmp_path: Path) -> None:
    rest = _adapter("AxumIngest", ("handle()",))
    arch = _arch((rest,), ())
    specs = {"rest_server_handler": _rust_tech_spec("rest_server_handler")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "src" / "main.rs"
    body = path.read_text()
    assert "#[tokio::main]" in body
    assert "async fn main()" in body
    assert "axum::serve" in body


def test_rust_emits_main_rs_for_consumer(tmp_path: Path) -> None:
    consumer = _adapter("RdkafkaConsumer", ("consume_raw()",))
    arch = _arch((consumer,), ())
    specs = {"message_queue_consumer": _rust_tech_spec("message_queue_consumer")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    body = path.read_text()
    assert "#[tokio::main]" in body
    assert "consumer started" in body


def test_rust_emits_default_skeleton_main_rs(tmp_path: Path) -> None:
    blob = _adapter("LocalBlob", ("put_blob()",))
    arch = _arch((blob,), ())
    specs = {"blob_storage": _rust_tech_spec("blob_storage")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    body = path.read_text()
    assert "#[tokio::main]" in body
    assert "service ready" in body


def test_java_emits_spring_boot_app(tmp_path: Path) -> None:
    rest = _adapter("EventIngestController", ("handle(body: str): dict",))
    arch = _arch((rest,), ())
    specs = {"rest_server_handler": _java_tech_spec("rest_server_handler")}
    path = WiringGenerator().generate(arch, specs, tmp_path)
    assert path == tmp_path / "src" / "main" / "java" / "com" / "example" / "App.java"
    body = path.read_text()
    assert "@SpringBootApplication" in body
    assert "SpringApplication.run(App.class, args)" in body
    assert "public class App" in body
