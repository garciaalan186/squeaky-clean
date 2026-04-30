"""Tests for RustImplementedClassParser."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.rust_implemented_class_parser import (
    RustImplementedClassParser,
)


def test_parses_pub_struct() -> None:
    raw = "```rust\npub struct EventId { value: String }\n```"
    body = RustImplementedClassParser().parse(raw, "EventId")
    assert "struct EventId" in body


def test_parses_pub_trait() -> None:
    raw = "```rust\npub trait Repository { fn save(&self); }\n```"
    body = RustImplementedClassParser().parse(raw, "Repository")
    assert "trait Repository" in body


def test_parses_pub_enum() -> None:
    raw = "```rust\npub enum Status { Open, Closed }\n```"
    body = RustImplementedClassParser().parse(raw, "Status")
    assert "enum Status" in body


def test_parses_private_struct() -> None:
    raw = "```rust\nstruct Helper;\n```"
    body = RustImplementedClassParser().parse(raw, "Helper")
    assert "struct Helper" in body


def test_parses_pub_type_alias() -> None:
    raw = "```rust\npub type UserId = String;\n```"
    body = RustImplementedClassParser().parse(raw, "UserId")
    assert "type UserId" in body


def test_strips_fence() -> None:
    raw = "```rust\npub struct A;\n```"
    body = RustImplementedClassParser().parse(raw, "A")
    assert "```" not in body


def test_raises_when_decl_missing() -> None:
    raw = "```rust\npub struct Other;\n```"
    with pytest.raises(ImplementedClassParseError):
        RustImplementedClassParser().parse(raw, "EventId")


def test_case_sensitive() -> None:
    raw = "```rust\npub struct eventid;\n```"
    with pytest.raises(ImplementedClassParseError):
        RustImplementedClassParser().parse(raw, "EventId")
