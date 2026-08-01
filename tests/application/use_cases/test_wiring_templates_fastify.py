"""Tests for the TypeScript (Fastify/Express) composition-root template."""

from squeaky_clean.application.generation.integration.wiring_templates_fastify import (
    render_fastify_main,
)


def test_express_technology_is_wired_with_express() -> None:
    code = render_fastify_main({"rest_server_handler": "express"})
    assert "import express from 'express';" in code
    assert "Fastify" not in code


def test_unspecified_technology_falls_back_to_fastify() -> None:
    code = render_fastify_main({"rest_server_handler": "unknown"})
    assert "import Fastify from 'fastify';" in code


def test_consumer_yields_typed_poll_skeleton() -> None:
    code = render_fastify_main({"message_queue_consumer": "kafkajs"})
    assert "consumer started" in code
    assert "(): void => undefined" in code


def test_no_inbound_category_yields_ready_skeleton() -> None:
    assert "service ready" in render_fastify_main({})
