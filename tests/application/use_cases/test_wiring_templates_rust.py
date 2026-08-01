"""Tests for the Rust composition-root template."""

from squeaky_clean.application.generation.integration.wiring_templates_rust import (
    render_rust_main,
)


def test_rest_handler_yields_axum_serve() -> None:
    code = render_rust_main({"rest_server_handler": object()})
    assert "axum::serve" in code
    assert "#[tokio::main]" in code


def test_consumer_yields_tokio_sleep_loop() -> None:
    code = render_rust_main({"message_queue_consumer": object()})
    assert "consumer started" in code
    assert "from_millis(100)" in code


def test_grpc_handler_yields_tonic_server() -> None:
    code = render_rust_main({"grpc_server_handler": object()})
    assert "tonic::transport::Server::builder" in code


def test_no_inbound_category_yields_ready_skeleton() -> None:
    code = render_rust_main({})
    assert "service ready" in code
    assert "from_secs(1)" in code
