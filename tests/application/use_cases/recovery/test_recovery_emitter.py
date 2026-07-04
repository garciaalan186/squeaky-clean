"""End-to-end test for RecoveryEmitter (front-half recovery for review)."""

from pathlib import Path

from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.recovery.recovery_emitter import RecoveryEmitter

_FILES = {
    "shop/__init__.py": "",
    "shop/domain/__init__.py": "",
    "shop/domain/order.py": (
        "from dataclasses import dataclass\n\n\n"
        "@dataclass\nclass Order:\n    id: str\n\n"
        "    def total(self) -> int:\n        return 0\n"
    ),
    "shop/domain/page.py": (
        "from django.db import models\n\n\n"
        "class Page(models.Model):\n    pass\n"
    ),
    "shop/tests/__init__.py": "",
    "shop/tests/test_order.py": (
        "from django.test import TestCase\n\n\n"
        "class OrderTest(TestCase):\n    def test_it(self) -> None:\n        pass\n"
    ),
}

_PURITY_FIRST = (
    "testability", "evolvability", "performance",
    "simplicity", "migration_safety", "delivery_speed",
)


def _run(tmp: Path) -> object:
    for rel, body in _FILES.items():
        path = tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    out = tmp / "out" / "recovered.squib"
    return RecoveryEmitter().emit(tmp, out, _PURITY_FIRST)


def test_excludes_test_classes_from_catalog(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    assert summary.classes == 2  # type: ignore[attr-defined]  # Order + Page, not OrderTest


def test_emits_a_parseable_squib(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    text = Path(summary.squib_path).read_text()  # type: ignore[attr-defined]
    assert ParseArchitectureNotation().parse(text).modules


def test_writes_refactor_sidecar_for_coupled_class(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    assert summary.proposals == 1  # type: ignore[attr-defined]  # Page(models.Model)
    sidecar = Path(summary.refactors_path).read_text()  # type: ignore[attr-defined]
    assert "Page" in sidecar and "PageRepository" in sidecar


def test_reports_mcda_recommendation(tmp_path: Path) -> None:
    summary = _run(tmp_path)
    assert summary.recommendation == "split"  # type: ignore[attr-defined]  # purity-first
