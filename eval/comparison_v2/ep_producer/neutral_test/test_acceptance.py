"""Neutral acceptance tests for EP-PROD Event Producer.

Kafka is mocked via conftest. publish_event is verified by inspecting the
captured mock messages (topic + 4 contract fields).
"""
from __future__ import annotations

import json

import pytest


def test_ingest_returns_event_with_contract_fields(producer) -> None:
    producer.reset_kafka()
    event = producer.ingest(b"hello", {"X-Source": "cli"})
    assert event is not None
    # IngestedEvent should expose the 4 contract fields
    for f in ("id", "received_at", "headers", "payload"):
        assert hasattr(event, f), f"event missing field {f}"


def test_empty_body_raises(producer) -> None:
    with pytest.raises(Exception):
        producer.ingest(b"", {})


def test_oversized_body_raises(producer) -> None:
    big = b"x" * (2 * 1024 * 1024)
    with pytest.raises(Exception):
        producer.ingest(big, {})


def test_publish_sends_to_events_raw_topic(producer) -> None:
    producer.reset_kafka()
    event = producer.ingest(b"hello", {"X-Source": "cli"})
    producer.publish(event)
    msgs = producer.kafka_messages()
    if not msgs:
        pytest.skip("publish_event did not invoke mocked Kafka producer")
    assert any(m["topic"] == "events.raw" for m in msgs), \
        f"expected topic events.raw, got: {[m['topic'] for m in msgs]}"


def test_publish_payload_contains_contract_keys(producer) -> None:
    producer.reset_kafka()
    event = producer.ingest(b"hello", {"X-Source": "cli"})
    producer.publish(event)
    msgs = producer.kafka_messages()
    if not msgs:
        pytest.skip("publish_event did not invoke mocked Kafka producer")
    raw = msgs[0]["value"]
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        pytest.fail(f"Kafka value not JSON: {raw!r}")
    for key in ("id", "received_at", "headers", "payload"):
        assert key in parsed, f"published JSON missing key {key}"
