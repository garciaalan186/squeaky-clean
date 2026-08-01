"""tech_spec_html_extractor: deterministic HTML→draft-TechSpec extractor."""

import re

from squeaky_clean.application.generation.techspec.tech_doc_format_unknown_error import (
    TechDocFormatUnknownError,
)
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget

_AWS_ANCHOR = re.compile(r"<a\s+id=[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']")
_SPHINX_METHOD = re.compile(
    r"<dl\s+class=[\"']py method[\"'][^>]*>.*?id=[\"']"
    r"([A-Za-z_][A-Za-z0-9_.]*)[\"']",
    re.IGNORECASE | re.DOTALL,
)
_GHP_SECTION = re.compile(
    r"<section\s+id=[\"']([A-Za-z_][A-Za-z0-9_-]*)[\"']", re.IGNORECASE,
)


class TechSpecHTMLExtractor:
    """Detects doc-site format then runs the matching extractor."""

    def extract(self, html: str, target: TechSpecTarget) -> dict[str, object]:
        """Return a draft TechSpec dict or raise TechDocFormatUnknownError."""
        for detector in (
            self._extract_aws, self._extract_sphinx, self._extract_github_pages,
        ):
            method = detector(html)
            if method is not None:
                return self._build(target, method)
        raise TechDocFormatUnknownError("no doc-site extractor matched")

    @staticmethod
    def _extract_aws(html: str) -> str | None:
        if "awsdocs-page-title" not in html:
            return None
        m = _AWS_ANCHOR.search(html)
        return m.group(1) if m else None

    @staticmethod
    def _extract_sphinx(html: str) -> str | None:
        if "py method" not in html:
            return None
        m = _SPHINX_METHOD.search(html)
        return m.group(1).rsplit(".", 1)[-1] if m else None

    @staticmethod
    def _extract_github_pages(html: str) -> str | None:
        if "<section" not in html.lower():
            return None
        m = _GHP_SECTION.search(html)
        return m.group(1).replace("-", "_") if m else None

    @staticmethod
    def _build(target: TechSpecTarget, method: str) -> dict[str, object]:
        return {
            "schema_version": "v1", "category": target.category,
            "technology": target.technology, "version_pin": target.version_pin,
            "language": "python",
            "install": {"manager": "pip", "package": target.version_pin},
            "imports": {"primary": f"import {target.technology}", "types": []},
            "client_construction": {
                "code": f"self._client = {target.technology}.Client()",
                "is_async": False, "thread_safe": True, "dependencies": [],
            },
            "primary_operations": [{
                "name": method, "signature": "() -> object",
                "sdk_call": f"self._client.{method}()",
                "error_types": ["RuntimeError"], "idempotency": "idempotent",
                "retry_policy": "none",
            }],
            "auth": {"method": "none", "env_vars": []},
        }
