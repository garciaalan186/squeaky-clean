"""Tests for MapConcernToSecurityEmitter."""

from squeaky_clean.application.generation.security.map_concern_to_security_icp import (
    MapConcernToSecurityEmitter,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
_M = MapConcernToSecurityEmitter()


def test_input_validation_maps_correctly() -> None:
    assert _M.map("input_validation", _PY) == (
        "python/security/InputValidationSecurityEmitter"
    )


def test_boundary_maps_correctly() -> None:
    assert _M.map("boundary", _PY) == "python/security/BoundarySecurityEmitter"


def test_error_handling_maps_correctly() -> None:
    assert _M.map("error_handling", _PY) == (
        "python/security/ErrorSafetySecurityEmitter"
    )


def test_injection_maps_correctly() -> None:
    assert _M.map("injection", _PY) == "python/security/InjectionSecurityEmitter"


def test_access_control_maps_correctly() -> None:
    assert _M.map("access_control", _PY) == (
        "python/security/AccessControlSecurityEmitter"
    )


def test_data_exposure_falls_back_to_access_control() -> None:
    assert _M.map("data_exposure", _PY) == (
        "python/security/AccessControlSecurityEmitter"
    )


def test_unknown_category_falls_back_to_access_control() -> None:
    assert _M.map("unknown_thing", _PY) == (
        "python/security/AccessControlSecurityEmitter"
    )
