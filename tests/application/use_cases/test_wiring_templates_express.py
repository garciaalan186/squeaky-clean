"""Tests for the JavaScript (Express) composition-root template."""

from squeaky_clean.application.generation.integration.wiring_templates_express import (
    render_express_main,
)


def test_rest_handler_yields_express_listen() -> None:
    code = render_express_main({"rest_server_handler": object()})
    assert "require('express')" in code
    assert "app.listen(port" in code


def test_consumer_yields_poll_skeleton() -> None:
    code = render_express_main({"message_queue_consumer": object()})
    assert "consumer started" in code
    assert "setInterval" in code


def test_no_inbound_category_yields_ready_skeleton() -> None:
    code = render_express_main({})
    assert "service ready" in code
