"""Unit tests for JSONLogger."""

import io
import json

from squeaky_clean.infrastructure.observability.json_logger import JSONLogger


def test_event_emits_one_json_line() -> None:
    buf = io.StringIO()
    JSONLogger(buf).event("agent_call", agent="architect", cost=0.05)
    line = buf.getvalue()
    assert line.endswith("\n")
    payload = json.loads(line)
    assert payload["kind"] == "agent_call"
    assert payload["agent"] == "architect"
    assert payload["cost"] == 0.05
    assert "ts" in payload


def test_event_drops_none_values() -> None:
    buf = io.StringIO()
    JSONLogger(buf).event("foo", a=1, b=None)
    payload = json.loads(buf.getvalue())
    assert "a" in payload
    assert "b" not in payload
