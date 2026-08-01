"""Tests for the Python composition-root templates and runtime dispatch."""

from squeaky_clean.application.generation.integration.wiring_templates_python import (
    render_default,
    render_flask,
    render_grpc_server,
    render_kafka_consumer_loop,
    render_runtime,
)


def test_render_flask_routes_post_to_handler() -> None:
    code = render_flask("handler", "use_case")
    assert "from flask import Flask" in code
    assert "handler.handle(payload)" in code
    assert "app.run(host=HOST, port=PORT)" in code


def test_render_kafka_loop_polls_and_executes() -> None:
    code = render_kafka_consumer_loop("consumer", "use_case")
    assert "consumer.poll_one(1.0)" in code
    assert "use_case.execute(msg)" in code
    assert "except KeyboardInterrupt" in code


def test_render_grpc_server_delegates_to_handler() -> None:
    code = render_grpc_server("handler")
    assert "grpc.server" in code
    assert "handler.serve(server)" in code


def test_render_runtime_prefers_rest_then_kafka_then_grpc() -> None:
    assert "Flask" in render_runtime("r", "k", "g", "u")
    assert "poll_one" in render_runtime(None, "k", "g", "u")
    assert "grpc.server" in render_runtime(None, None, "g", "u")
    assert render_runtime(None, None, None, "u") == render_default()
