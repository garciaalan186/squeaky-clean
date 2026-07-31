"""Tests for ReplicateCalibrationError."""

from squeaky_clean.interface.cli.replicates.replicate_calibration_error import (
    ReplicateCalibrationError,
)


def test_is_runtime_error() -> None:
    assert issubclass(ReplicateCalibrationError, RuntimeError)
