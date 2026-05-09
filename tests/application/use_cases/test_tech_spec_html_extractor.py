"""Tests for TechSpecHTMLExtractor (H4)."""

import pytest

from squeaky_clean.application.use_cases.tech_spec_html_extractor import (
    TechDocFormatUnknownError,
    TechSpecHTMLExtractor,
)


def test_extractor_handles_aws_docs_format() -> None:
    html = (
        "<h1 class=\"awsdocs-page-title\">PutObject</h1>"
        "<a id=\"put_object\">link</a>"
    )
    spec = TechSpecHTMLExtractor().extract(
        html, "blob_storage", "s3", "boto3==1.40",
    )
    assert spec["technology"] == "s3"
    ops = spec["primary_operations"]
    assert isinstance(ops, list)
    assert ops[0]["name"] == "put_object"


def test_extractor_handles_sphinx_format() -> None:
    html = (
        "<dl class=\"py method\"><dt id=\"client.get_object\">"
        "get_object</dt></dl>"
    )
    spec = TechSpecHTMLExtractor().extract(
        html, "blob_storage", "s3", "boto3==1.40",
    )
    ops = spec["primary_operations"]
    assert isinstance(ops, list)
    assert ops[0]["name"] == "get_object"


def test_extractor_handles_github_pages_format() -> None:
    html = "<section id=\"do-thing\"><h2>do_thing</h2></section>"
    spec = TechSpecHTMLExtractor().extract(
        html, "blob_storage", "x", "v1",
    )
    ops = spec["primary_operations"]
    assert isinstance(ops, list)
    assert ops[0]["name"] == "do_thing"


def test_extractor_raises_on_unknown_format() -> None:
    with pytest.raises(TechDocFormatUnknownError):
        TechSpecHTMLExtractor().extract(
            "<html>plain text</html>", "blob_storage", "x", "v1",
        )
