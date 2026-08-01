"""Tests for ManifestWriteError (R6.8 manifest error contract)."""

import pytest

from squeaky_clean.application.generation.integration.manifests.manifest_write_error import (
    ManifestWriteError,
)


def test_is_a_runtime_error_with_reason() -> None:
    err = ManifestWriteError("package.json write failed: disk full")
    assert isinstance(err, RuntimeError)
    assert "disk full" in str(err)


def test_catchable_alongside_oserror() -> None:
    # The ManifestEmitter contract: except (OSError, ManifestWriteError).
    caught = None
    try:
        raise ManifestWriteError("boom")
    except (OSError, ManifestWriteError) as exc:
        caught = exc
    assert isinstance(caught, ManifestWriteError)


def test_is_not_an_oserror() -> None:
    # Deliberately NOT an OSError subclass: generators translate OSError
    # into this type; it must not be re-caught as one upstream.
    assert not issubclass(ManifestWriteError, OSError)
    with pytest.raises(ManifestWriteError):
        raise ManifestWriteError("x")
