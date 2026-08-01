"""wiring_templates_rust: Rust composition-root src/main.rs renderer."""

from __future__ import annotations


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
