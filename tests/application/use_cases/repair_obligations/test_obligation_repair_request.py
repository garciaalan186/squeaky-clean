"""Tests for the ObligationRepairRequest DTO."""

import dataclasses
from pathlib import Path

from squeaky_clean.application.generation.repair.obligations.obligation_repair_request import (
    ObligationRepairRequest,
)


def test_request_is_frozen_with_the_four_fields(tmp_path: Path) -> None:
    request = ObligationRepairRequest((), tmp_path, None, 2)
    assert request.obligations == ()
    assert request.output_dir == tmp_path
    assert request.toolkit is None
    assert request.max_passes == 2
    fields = {f.name for f in dataclasses.fields(ObligationRepairRequest)}
    assert fields == {"obligations", "output_dir", "toolkit", "max_passes"}
