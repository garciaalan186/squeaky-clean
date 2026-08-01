"""Tests for the Go composition-root template."""

from squeaky_clean.application.generation.integration.wiring_templates_go import (
    render_go_main,
)


def test_rest_handler_yields_listen_and_serve() -> None:
    code = render_go_main({"rest_server_handler": object()})
    assert "http.ListenAndServe" in code
    assert code.startswith("// Auto-generated composition root")


def test_consumer_yields_signal_based_shutdown_loop() -> None:
    code = render_go_main({"message_queue_consumer": object()})
    assert "signal.Notify" in code
    assert "shutting down" in code


def test_no_inbound_category_yields_sleep_skeleton() -> None:
    code = render_go_main({})
    assert "service ready" in code
    assert "time.Sleep(time.Second)" in code
