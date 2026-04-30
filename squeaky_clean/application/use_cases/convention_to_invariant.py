"""ConventionToInvariant: maps known convention tags to INVARIANT strings."""

_CONVENTIONS: dict[str, str] = {
    "timeline_includes_self":
        "a user's timeline must include the user's own posts",
    "follow_asymmetric":
        "a follow relation is one-directional; reverse direction is independent",
    "auth_session_single_active":
        "at most one active session per user; new login invalidates prior sessions",
    "unique_by_natural_key":
        "domain entities with a natural key reject duplicates",
    "soft_delete_preserves_history":
        "delete operations mark records inactive; data is never physically removed",
    "idempotent_retries_safe":
        "command operations succeed identically when retried with the same inputs",
    "single_use_authorization_code":
        "an authorization code is consumed at first exchange and cannot be reused",
    "refresh_token_rotation":
        "exchanging a refresh token issues a new refresh token and invalidates the old one",
    "redirect_uri_strict_match":
        "redirect_uri must match the value registered with the client byte-for-byte",
}


class UnknownConventionError(ValueError):
    """Raised when a convention tag has no registered expansion."""


class ConventionToInvariant:
    """Looks up the §Notation INVARIANT text for a given convention tag."""

    def lookup(self, tag: str) -> str:
        """Return the INVARIANT expansion for ``tag``; raise on unknown tags."""
        if tag not in _CONVENTIONS:
            raise UnknownConventionError(
                f"unknown domain convention tag: {tag!r}; known tags: "
                f"{sorted(_CONVENTIONS)}"
            )
        return _CONVENTIONS[tag]
