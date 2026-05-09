"""Tests for OriginAllowlist (H4)."""

from squeaky_clean.application.use_cases.origin_allowlist import OriginAllowlist


def test_allowlist_accepts_url_with_matching_prefix() -> None:
    allow = OriginAllowlist(("https://docs.aws.amazon.com/",))
    assert allow.is_allowed("https://docs.aws.amazon.com/AmazonS3/page.html")


def test_allowlist_rejects_unmatched_url() -> None:
    allow = OriginAllowlist(("https://docs.aws.amazon.com/",))
    assert not allow.is_allowed("https://random-blogpost.com/aws.html")


def test_allowlist_rejects_when_empty() -> None:
    allow = OriginAllowlist(())
    assert not allow.is_allowed("https://docs.aws.amazon.com/foo")


def test_allowlist_strict_prefix_no_partial_wildcards() -> None:
    allow = OriginAllowlist(("https://docs.aws.amazon.com/AmazonS3/",))
    assert not allow.is_allowed("https://docs.aws.amazon.com/EC2/page")
    assert allow.is_allowed("https://docs.aws.amazon.com/AmazonS3/x")
