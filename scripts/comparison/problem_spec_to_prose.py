"""Deterministic ProblemSpec → prose-prompt translator (framings 2 + 3).

Pure function; no LLM. Version-pinned: any change to the template bumps
TRANSLATOR_VERSION and that version is recorded on every comparison run
so methodology drift is traceable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TRANSLATOR_VERSION = "v1"


@dataclass(frozen=True)
class TranslationResult:
    """Prose prompt + translator version stamp."""

    prompt: str
    version: str


def translate(problem_spec_path: Path) -> TranslationResult:
    """Render the JSON ProblemSpec at `problem_spec_path` as a prose prompt."""
    spec = json.loads(problem_spec_path.read_text())
    body = "\n".join(_sections(spec))
    return TranslationResult(prompt=body, version=TRANSLATOR_VERSION)


def _sections(spec: dict[str, Any]) -> list[str]:
    out: list[str] = ["You are generating a Python project. Below is the full specification.\n"]
    out.append(_identity(spec))
    out.append(_contexts(spec))
    out.append(_criteria(spec))
    out.append(_patterns(spec))
    out.append(_infrastructure(spec))
    out.append(_conventions(spec))
    out.append(_data_classification(spec))
    out.append(_contracts(spec))
    out.append(_target_language(spec))
    out.append(_output_format())
    return [s for s in out if s]


def _identity(spec: dict[str, Any]) -> str:
    return (
        "PROJECT IDENTITY\n"
        f"  ID:          {spec.get('id', '')}\n"
        f"  Description: {spec.get('description', '')}"
    )


def _contexts(spec: dict[str, Any]) -> str:
    items = spec.get("required_bounded_contexts", [])
    if not items:
        return ""
    lines = "\n".join(f"  - {ctx}" for ctx in items)
    return f"BOUNDED CONTEXTS (use these as module names, verbatim)\n{lines}"


def _criteria(spec: dict[str, Any]) -> str:
    items = spec.get("acceptance_criteria", [])
    if not items:
        return ""
    lines = "\n".join(f"  {i + 1}. {c}" for i, c in enumerate(items))
    return f"ACCEPTANCE CRITERIA (every Gherkin scenario must be satisfied by your code)\n{lines}"


def _patterns(spec: dict[str, Any]) -> str:
    items = spec.get("required_patterns", [])
    if not items:
        return ""
    lines = "\n".join(f"  - {p}" for p in items)
    return f"REQUIRED PATTERNS (use the GoF/DDD pattern catalog)\n{lines}"


def _infrastructure(spec: dict[str, Any]) -> str:
    items = spec.get("infrastructure_choices", [])
    if not items:
        return ""
    lines = "\n".join(
        f"  - category={c.get('category')}, technology={c.get('technology')}, "
        f"version={c.get('version_pin', '')}"
        for c in items
    )
    return f"INFRASTRUCTURE CHOICES (use these specific SDKs and version pins)\n{lines}"


def _conventions(spec: dict[str, Any]) -> str:
    items = spec.get("domain_conventions", [])
    if not items:
        return ""
    lines = "\n".join(f"  - {tag}" for tag in items)
    return f"DOMAIN CONVENTIONS (each tag corresponds to a canonical invariant; honor it)\n{lines}"


def _data_classification(spec: dict[str, Any]) -> str:
    items = spec.get("data_classification", [])
    if not items:
        return ""
    lines = "\n".join(
        f"  - {entry.get('field_ref')}: {entry.get('sensitivity')}"
        for entry in items
    )
    return f"DATA CLASSIFICATION (treat these field references with the indicated sensitivity)\n{lines}"


def _contracts(spec: dict[str, Any]) -> str:
    produces = spec.get("produces_contracts", [])
    consumes = spec.get("consumes_contracts", [])
    if not produces and not consumes:
        return ""
    return f"CROSS-SERVICE CONTRACTS\n  Produces: {produces}\n  Consumes: {consumes}"


def _target_language(spec: dict[str, Any]) -> str:
    lang = spec.get("target_language", "python")
    return f"TARGET LANGUAGE: {lang}"


def _output_format() -> str:
    return (
        "OUTPUT FORMAT\n"
        "  Emit each source file as a fenced code block immediately preceded by a\n"
        "  header line of the form `### File: path/to/file.py`. The project should\n"
        "  follow Clean Architecture layers under src/domain/, src/application/,\n"
        "  src/infrastructure/, src/interface/. Emit one class per file.\n"
        "  Also emit a tests/conftest.py that exposes a `discover_implementation()`\n"
        "  function returning a dict mapping behavior names (derived from the\n"
        "  acceptance criteria verbs) to concrete callables. Emit nothing outside\n"
        "  the code blocks."
    )
