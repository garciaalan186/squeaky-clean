"""OTelLogger: emit OpenTelemetry-style structured spans alongside JSONLogger.

If `opentelemetry` is installed and `OTEL_EXPORTER_OTLP_ENDPOINT` is set,
the spans are sent to the configured backend. Otherwise the logger
degrades to a JSON-line emitter — so removing this dependency from a
pipeline is purely a config change.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import IO

from squeaky_clean.infrastructure.observability.json_logger import JSONLogger


class OTelLogger:
    """Span emitter; uses opentelemetry if available, falls back to JSONLogger."""

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._fallback: JSONLogger = JSONLogger(stream)
        self._otel = self._try_import_otel()

    @contextmanager
    def span(self, name: str, **attrs: object):  # type: ignore[no-untyped-def]
        """Open a span; emits start + end events with cost / duration / cache."""
        start = time.monotonic()
        otel = self._otel
        if otel is not None:
            scope = otel.start_as_current_span(name)  # type: ignore[attr-defined]
            with scope as span:
                for k, v in attrs.items():
                    span.set_attribute(k, str(v))
                try:
                    yield span
                finally:
                    span.set_attribute(
                        "duration_ms",
                        int((time.monotonic() - start) * 1000),
                    )
        else:
            self._fallback.event(f"{name}:start", **attrs)
            try:
                yield None
            finally:
                self._fallback.event(
                    f"{name}:end",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )

    def _try_import_otel(self) -> object | None:
        if "OTEL_EXPORTER_OTLP_ENDPOINT" not in os.environ:
            return None
        try:
            from opentelemetry import trace  # type: ignore[import-not-found]
            return trace.get_tracer("squeaky-clean")  # type: ignore[no-any-return]
        except (ImportError, AttributeError):
            return None
