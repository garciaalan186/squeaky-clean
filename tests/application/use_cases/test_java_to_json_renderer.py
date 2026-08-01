"""Tests for JavaToJsonRenderer (extracted from EmitJavaEntitySerialization)."""

from squeaky_clean.application.shared.language.java_to_json_renderer import (
    JavaToJsonRenderer,
)


def test_renders_method_with_exact_declared_keys() -> None:
    body = JavaToJsonRenderer().render([
        ("received_at", "receivedAt", "str"),
        ("size_bytes", "sizeBytes", "raw"),
    ])
    assert "public String toJson()" in body
    # JSON keys keep declared snake_case; accessors use camelCase.
    assert '\\"received_at\\"' in body
    assert "toJsonStr(this.receivedAt)" in body
    assert "String.valueOf(this.sizeBytes)" in body


def test_map_fields_route_through_map_helper() -> None:
    body = JavaToJsonRenderer().render([("tags", "tags", "map")])
    assert "toJsonMap(this.tags)" in body


def test_helpers_are_always_appended() -> None:
    body = JavaToJsonRenderer().render([])
    assert "private static String toJsonStr(String v)" in body
    assert "private static String toJsonMap(java.util.Map<String, String> m)" in body


def test_only_first_field_omits_leading_comma() -> None:
    body = JavaToJsonRenderer().render([
        ("a", "a", "raw"), ("b", "b", "raw"),
    ])
    assert 'sb.append("\\"a\\":")' in body
    assert 'sb.append(",\\"b\\":")' in body
