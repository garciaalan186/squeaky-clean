"""Unit tests for SecretScanner."""

from squeaky_clean.application.use_cases.secret_scanner import SecretScanner


def test_clean_text_returns_empty() -> None:
    assert SecretScanner().scan("hello world") == ()


def test_anthropic_key_detected() -> None:
    bad = "key = 'sk-ant-api03-abcdef0123456789ABCDEF'"  # secret-scan: allow
    hits = SecretScanner().scan(bad)
    assert "anthropic_api_key" in hits


def test_aws_key_detected() -> None:
    hits = SecretScanner().scan("AKIAIOSFODNN7EXAMPLE")  # secret-scan: allow
    assert "aws_access_key" in hits


def test_password_assignment_detected() -> None:
    hits = SecretScanner().scan("password = 'hunter2'")  # secret-scan: allow
    assert "password_assignment" in hits
