"""wiring_templates: per-runtime-shape main.py renderers (Flask / Kafka / gRPC / Spring Boot)."""

from __future__ import annotations


def _entry_header() -> str:
    return ('if __name__ == "__main__":\n'
            "    HOST = os.environ.get(\"SERVICE_HOST\", \"127.0.0.1\")\n"
            "    PORT = int(os.environ.get(\"SERVICE_PORT\", \"8000\"))\n")


def render_flask(handler_var: str, use_case_var: str) -> str:
    """Emit a Flask app block routing POST / to the inbound handler."""
    return (
        "from flask import Flask, request, jsonify\n"
        "app = Flask(__name__)\n\n"
        "def _route() -> object:\n"
        "    payload = request.get_json(silent=True) or {}\n"
        f"    result = {handler_var}.handle(payload)\n"
        "    return jsonify(result)\n\n"
        "app.add_url_rule(\"/\", \"root\", _route, methods=[\"POST\"])\n\n"
        + _entry_header()
        + "    app.run(host=HOST, port=PORT)\n"
    )


def render_kafka_consumer_loop(consumer_var: str, use_case_var: str) -> str:
    """Emit a polling consume loop with KeyboardInterrupt-graceful shutdown."""
    return (
        _entry_header()
        + "    try:\n"
        "        while True:\n"
        f"            msg = {consumer_var}.poll_one(1.0)\n"
        "            if msg is None:\n"
        "                continue\n"
        f"            {use_case_var}.execute(msg)\n"
        "    except KeyboardInterrupt:\n"
        "        pass\n"
    )


def render_grpc_server(handler_var: str) -> str:
    """Emit a minimal grpc.server bootstrap that delegates to the handler."""
    return (
        "import grpc\n"
        "from concurrent import futures\n\n"
        + _entry_header()
        + "    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))\n"
        f"    server.add_insecure_port(f\"{{HOST}}:{{PORT}}\")\n"
        f"    {handler_var}.serve(server)\n"
        "    server.start()\n"
        "    server.wait_for_termination()\n"
    )


def render_default() -> str:
    """Emit a no-runtime skeleton so the file is still executable Python."""
    return (
        'if __name__ == "__main__":\n'
        "    # TODO: no inbound entry point detected by WiringGenerator.\n"
        "    pass\n"
    )


def render_runtime(
    rest_var: str | None,
    kafka_var: str | None,
    grpc_var: str | None,
    use_case_var: str,
) -> str:
    """Pick the right runtime block based on which inbound adapter exists."""
    if rest_var is not None:
        return render_flask(rest_var, use_case_var)
    if kafka_var is not None:
        return render_kafka_consumer_loop(kafka_var, use_case_var)
    if grpc_var is not None:
        return render_grpc_server(grpc_var)
    return render_default()


def render_go_main(tech_specs: dict[str, object]) -> str:
    """Emit a Go composition root ``main.go`` for Go TechSpec runtimes.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> http.ListenAndServe; message_queue_consumer ->
    signal-based shutdown loop; otherwise a sleep skeleton.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    head = ("// Auto-generated composition root (WiringGenerator).\n"
            "package main\n\nimport (\n\t\"log\"\n\t\"net/http\"\n"
            "\t\"os\"\n\t\"os/signal\"\n\t\"syscall\"\n\t\"time\"\n)\n\n")
    if rest:
        body = ("func main() {\n\taddr := os.Getenv(\"SERVICE_ADDR\")\n"
                "\tif addr == \"\" { addr = \":8080\" }\n"
                "\tlog.Printf(\"listening on %s\", addr)\n"
                "\tif err := http.ListenAndServe(addr, nil); err != nil "
                "{ log.Fatal(err) }\n}\n")
    elif consumer:
        body = ("func main() {\n\tsigs := make(chan os.Signal, 1)\n"
                "\tsignal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)\n"
                "\tlog.Println(\"consumer started\")\n"
                "\tfor {\n\t\tselect {\n\t\tcase <-sigs:\n"
                "\t\t\tlog.Println(\"shutting down\"); return\n"
                "\t\tdefault: time.Sleep(100 * time.Millisecond)\n"
                "\t\t}\n\t}\n}\n")
    else:
        body = ("func main() {\n\tlog.Println(\"service ready\")\n"
                "\tfor { time.Sleep(time.Second) }\n}\n")
    return head + body


def render_rust_main(tech_specs: dict[str, object]) -> str:
    """Emit a Rust composition root ``src/main.rs`` for Rust TechSpec runtimes.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> axum::serve; message_queue_consumer -> tokio
    recv loop; grpc_server_handler -> tonic Server::builder; otherwise a
    tokio sleep skeleton. Always uses ``#[tokio::main]`` since most async
    Rust SDKs (aws-sdk, redis, tonic, rdkafka) require a tokio runtime.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    grpc = "grpc_server_handler" in tech_specs
    head = ("// Auto-generated composition root (WiringGenerator).\n"
            "use std::env;\n\n"
            "#[tokio::main]\n"
            "async fn main() -> Result<(), Box<dyn std::error::Error>> {\n"
            "    let addr = env::var(\"SERVICE_ADDR\")"
            ".unwrap_or_else(|_| \":8080\".to_string());\n")
    if rest:
        body = ("    let listener = tokio::net::TcpListener::bind(&addr)"
                ".await?;\n"
                "    let app = axum::Router::new();\n"
                "    axum::serve(listener, app).await?;\n"
                "    Ok(())\n}\n")
    elif consumer:
        body = ("    println!(\"consumer started on {}\", addr);\n"
                "    loop {\n"
                "        tokio::time::sleep("
                "tokio::time::Duration::from_millis(100)).await;\n"
                "    }\n"
                "}\n")
    elif grpc:
        body = ("    let socket = addr.parse()?;\n"
                "    tonic::transport::Server::builder()\n"
                "        .serve(socket).await?;\n"
                "    Ok(())\n}\n")
    else:
        body = ("    println!(\"service ready on {}\", addr);\n"
                "    loop {\n"
                "        tokio::time::sleep("
                "tokio::time::Duration::from_secs(1)).await;\n"
                "    }\n"
                "}\n")
    return head + body


def render_express_main(tech_specs: dict[str, object]) -> str:
    """Emit a JavaScript composition root ``index.js`` for JS TechSpec runtimes.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> Express ``app.listen``; message_queue_consumer
    -> ``setInterval`` poll skeleton; otherwise an empty server skeleton.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    head = "// Auto-generated composition root (WiringGenerator).\n"
    if rest:
        return (head
                + "const express = require('express');\n"
                + "const app = express();\n"
                + "app.use(express.json());\n"
                + "const port = process.env.SERVICE_PORT || 8000;\n"
                + "app.post('/', (req, res) => res.status(200).json({}));\n"
                + "app.listen(port, () => console.log(`listening on ${port}`));\n")
    if consumer:
        return (head
                + "console.log('consumer started');\n"
                + "setInterval(() => {}, 1000);\n")
    return (head + "console.log('service ready');\n"
            + "setInterval(() => {}, 1000);\n")


def render_fastify_main(tech_specs: dict[str, object]) -> str:
    """Emit a TypeScript composition root ``src/index.ts`` for TS TechSpecs.

    Picks the runtime from inbound categories present in ``tech_specs``:
    rest_server_handler -> Fastify ``listen``; message_queue_consumer ->
    ``setInterval`` poll skeleton; otherwise an empty server skeleton.
    """
    rest = "rest_server_handler" in tech_specs
    consumer = "message_queue_consumer" in tech_specs
    head = "// Auto-generated composition root (WiringGenerator).\n"
    if rest:
        return (head
                + "import Fastify from 'fastify';\n\n"
                + "const app = Fastify({ logger: true });\n"
                + "const port = Number(process.env.SERVICE_PORT ?? 8000);\n"
                + "app.post('/', async () => ({}));\n"
                + "app.listen({ port, host: '0.0.0.0' });\n")
    if consumer:
        return (head
                + "console.log('consumer started');\n"
                + "setInterval((): void => undefined, 1000);\n")
    return (head + "console.log('service ready');\n"
            + "setInterval((): void => undefined, 1000);\n")


def render_spring_boot_main() -> str:
    """Emit a Spring Boot composition root.

    Spring's component scanning + @Bean configuration handles the wiring
    of @RestController / @KafkaListener / etc. — so the Java composition
    root is the @SpringBootApplication bootstrap class plus a few @Bean
    factories for non-Spring-managed adapters (e.g. blob stores).

    The body is intentionally minimal: a real project gains @Bean methods
    for outbound adapters (BlobStore, KafkaTemplate, etc.) but those are
    auto-configured by Spring Boot starter modules in the common path.
    """
    return (
        "// App: Spring Boot composition root (auto-wires @RestController / @KafkaListener).\n"
        "package com.example;\n"
        "\n"
        "import org.springframework.boot.SpringApplication;\n"
        "import org.springframework.boot.autoconfigure.SpringBootApplication;\n"
        "import org.springframework.kafka.annotation.EnableKafka;\n"
        "\n"
        "@SpringBootApplication\n"
        "@EnableKafka\n"
        "public class App {\n"
        "    public static void main(String[] args) {\n"
        "        SpringApplication.run(App.class, args);\n"
        "    }\n"
        "}\n"
    )
