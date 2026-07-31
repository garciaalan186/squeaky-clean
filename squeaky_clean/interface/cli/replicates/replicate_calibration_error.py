"""ReplicateCalibrationError: every replicate of a calibration failed."""

from __future__ import annotations


class ReplicateCalibrationError(RuntimeError):
    """Raised when no replicate of an N-replicate run produced a result.

    Individual replicate failures are isolated (recorded in
    replicate_summary as exclusions); this fires only when there is
    nothing left to aggregate.
    """
