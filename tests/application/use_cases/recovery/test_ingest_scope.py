"""Tests for IngestScope (test/vendored-dir exclusion)."""

from pathlib import Path

from squeaky_clean.application.use_cases.recovery.ingest_scope import IngestScope


def _includes(rel: str) -> bool:
    root = Path("/proj")
    return IngestScope().includes(root / rel, root)


def test_production_module_is_included() -> None:
    assert _includes("shop/domain/order.py") is True


def test_test_prefixed_file_is_excluded() -> None:
    assert _includes("shop/test_order.py") is False


def test_suffixed_test_file_is_excluded() -> None:
    assert _includes("shop/order_test.py") is False


def test_files_under_a_tests_dir_are_excluded() -> None:
    assert _includes("shop/tests/test_order.py") is False
    assert _includes("shop/tests/factories.py") is False


def test_django_style_tests_module_is_excluded() -> None:
    assert _includes("shop/tests.py") is False


def test_conftest_and_setup_are_excluded() -> None:
    assert _includes("conftest.py") is False
    assert _includes("setup.py") is False


def test_vendored_and_build_dirs_are_excluded() -> None:
    assert _includes(".venv/lib/site-packages/django/db/models.py") is False
    assert _includes("node_modules/pkg/x.py") is False
    assert _includes("build/lib/thing.py") is False
    assert _includes("wagtail.egg-info/foo.py") is False


def test_migrations_are_excluded() -> None:
    assert _includes("shop/migrations/0001_initial.py") is False
