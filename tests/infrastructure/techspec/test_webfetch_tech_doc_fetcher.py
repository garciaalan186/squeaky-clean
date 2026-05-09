"""Tests for WebFetchTechDocFetcher (H4)."""

import http.server
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from squeaky_clean.domain.interfaces.tech_doc_fetcher import TechDocFetchError
from squeaky_clean.infrastructure.techspec.webfetch_tech_doc_fetcher import (
    WebFetchTechDocFetcher,
)


class _StubHandler(BaseHTTPRequestHandler):
    body: bytes = b"<html>ok</html>"
    content_type: str = "text/html"

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", self.content_type)
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *_args: object, **_kw: object) -> None:
        return


def _start_server(handler: type[BaseHTTPRequestHandler]) -> HTTPServer:
    srv = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_fetch_returns_body_for_html() -> None:
    srv = _start_server(_StubHandler)
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/x"
        body = WebFetchTechDocFetcher().fetch(url)
        assert "<html>ok</html>" in body
    finally:
        srv.shutdown()


def test_fetch_rejects_disallowed_content_type() -> None:
    class _BadType(_StubHandler):
        content_type = "application/octet-stream"

    srv = _start_server(_BadType)
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/x"
        with pytest.raises(TechDocFetchError):
            WebFetchTechDocFetcher().fetch(url)
    finally:
        srv.shutdown()


def test_fetch_rejects_oversize_response() -> None:
    class _Big(_StubHandler):
        body = b"a" * (200 * 1024)

    srv = _start_server(_Big)
    try:
        url = f"http://127.0.0.1:{srv.server_address[1]}/x"
        with pytest.raises(TechDocFetchError):
            WebFetchTechDocFetcher().fetch(url)
    finally:
        srv.shutdown()


def test_fetch_raises_on_unreachable_host() -> None:
    with pytest.raises(TechDocFetchError):
        WebFetchTechDocFetcher(timeout_seconds=0.5).fetch(
            "http://127.0.0.1:1/never"
        )
