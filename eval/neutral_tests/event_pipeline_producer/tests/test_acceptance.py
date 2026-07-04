"""Acceptance test suite.

Each test looks up a behavior key from ``discover_implementation()`` (provided
by the project's ``tests/conftest.py``).  If the key is missing the test is
skipped — that's a structural mismatch we want to count separately from real
assertion failures.

Tests prefer property-style assertions (type, attributes, invariants) over
exact-string equality so different implementations can both pass.
"""

import json
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(impl, key):
    """Return impl[key] or skip the test if missing."""
    if not isinstance(impl, dict):
        pytest.skip(
            f"discover_implementation() did not return a dict (got {type(impl)!r})"
        )
    if key not in impl:
        pytest.skip(f"implementation missing required key {key!r}")
    return impl[key]


def _has_field(obj, name):
    """True if obj exposes attribute or mapping key `name`."""
    if hasattr(obj, name):
        return True
    try:
        return name in obj
    except TypeError:
        return False


def _field(obj, name):
    if hasattr(obj, name):
        return getattr(obj, name)
    return obj[name]


# ---------------------------------------------------------------------------
# Criterion 1: ingest_event returns an IngestedEvent for a valid request
# ---------------------------------------------------------------------------

def test_ingest_event_returns_ingested_event(implementation):
    ingest_event = _get(implementation, "ingest_event")
    ingested_event_type = _get(implementation, "IngestedEvent")

    body = b"hello"
    headers = {"X-Source": "cli"}

    result = ingest_event(body=body, headers=headers)

    assert isinstance(result, ingested_event_type), (
        f"expected IngestedEvent instance, got {type(result)!r}"
    )

    # Property-style: the event should expose the canonical fields.
    for fname in ("id", "received_at", "headers", "payload"):
        assert _has_field(result, fname), f"IngestedEvent missing field {fname!r}"


# ---------------------------------------------------------------------------
# Criterion 2: empty body raises
# ---------------------------------------------------------------------------

def test_ingest_event_rejects_empty_body(implementation):
    ingest_event = _get(implementation, "ingest_event")

    with pytest.raises(Exception):
        ingest_event(body=b"", headers={"X-Source": "cli"})


# ---------------------------------------------------------------------------
# Criterion 3: body larger than 1 MB raises
# ---------------------------------------------------------------------------

def test_ingest_event_rejects_oversized_body(implementation):
    ingest_event = _get(implementation, "ingest_event")

    too_big = b"x" * (1024 * 1024 + 1)  # 1 MB + 1 byte

    with pytest.raises(Exception):
        ingest_event(body=too_big, headers={"X-Source": "cli"})


# ---------------------------------------------------------------------------
# Criterion 4: publish_event sends to 'events.raw' with the right JSON shape
# ---------------------------------------------------------------------------

def test_publish_event_sends_to_events_raw_topic(implementation):
    publish_event = _get(implementation, "publish_event")
    make_event = _get(implementation, "make_ingested_event")
    make_producer = _get(implementation, "make_fake_producer")

    producer = make_producer()  # captures published messages
    event = make_event(body=b"hello", headers={"X-Source": "cli"})

    publish_event(event, producer=producer)

    # The fake producer is expected to expose `.messages`: a list of
    # (topic, payload_bytes_or_str) tuples or dict-like records.
    assert hasattr(producer, "messages"), (
        "fake producer must expose `.messages` capturing publishes"
    )
    assert len(producer.messages) >= 1, "no message was published"

    msg = producer.messages[-1]

    # Accept either tuple (topic, payload) or dict-like {topic, value}.
    if isinstance(msg, tuple):
        topic, payload = msg[0], msg[1]
    else:
        topic = msg.get("topic") if hasattr(msg, "get") else _field(msg, "topic")
        payload = (
            msg.get("value")
            if hasattr(msg, "get") and "value" in msg
            else _field(msg, "value")
        )

    assert topic == "events.raw", f"expected topic 'events.raw', got {topic!r}"

    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8")
    if isinstance(payload, str):
        payload = json.loads(payload)

    assert isinstance(payload, dict), f"payload should decode to a dict, got {type(payload)!r}"
    for key in ("id", "received_at", "headers", "payload"):
        assert key in payload, f"published JSON missing key {key!r}"


# ---------------------------------------------------------------------------
# Criterion 5: Kafka unreachable raises
# ---------------------------------------------------------------------------

def test_publish_event_raises_when_kafka_unreachable(implementation):
    publish_event = _get(implementation, "publish_event")
    make_event = _get(implementation, "make_ingested_event")
    make_broken = _get(implementation, "make_unreachable_producer")

    producer = make_broken()
    event = make_event(body=b"hello", headers={"X-Source": "cli"})

    with pytest.raises(Exception):
        publish_event(event, producer=producer)
