"""Neutral acceptance tests for P5 OAuth2 Server."""
from __future__ import annotations

import pytest


def test_register_client_returns_client(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    assert client is not None
    # Loose check: object has some "client" identity
    assert (
        getattr(client, "id", None) is not None
        or getattr(client, "client_id", None) is not None
        or getattr(client, "name", None) is not None
    )


def test_issue_code_returns_authorization_code(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    code = oauth.issue_code(client, "https://app1/cb")
    assert code is not None


def test_issue_code_wrong_redirect_raises(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    with pytest.raises(Exception):
        oauth.issue_code(client, "https://evil")


def test_exchange_code_returns_access_token(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    code = oauth.issue_code(client, "https://app1/cb")
    token = oauth.exchange_code(code)
    assert token is not None


def test_exchange_already_used_code_raises(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    code = oauth.issue_code(client, "https://app1/cb")
    oauth.exchange_code(code)
    with pytest.raises(Exception):
        oauth.exchange_code(code)


def test_refresh_returns_new_access_token(oauth) -> None:
    client = oauth.register_client("app1", "https://app1/cb")
    code = oauth.issue_code(client, "https://app1/cb")
    access = oauth.exchange_code(code)
    rt = oauth.refresh_token_from_access(access)
    if rt is None:
        pytest.skip("AccessToken did not expose a refresh_token attribute")
    new_access = oauth.refresh(rt)
    assert new_access is not None


def test_revoked_refresh_raises(oauth) -> None:
    if not oauth.has_revoke():
        pytest.skip("No revoke API exposed")
    client = oauth.register_client("app1", "https://app1/cb")
    code = oauth.issue_code(client, "https://app1/cb")
    access = oauth.exchange_code(code)
    rt = oauth.refresh_token_from_access(access)
    if rt is None:
        pytest.skip("AccessToken did not expose a refresh_token attribute")
    oauth.revoke_refresh(rt)
    with pytest.raises(Exception):
        oauth.refresh(rt)
