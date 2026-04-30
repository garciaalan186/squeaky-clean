"""Unit tests for RunManifest."""

import json
from pathlib import Path

from squeaky_clean.application.use_cases.run_manifest import RunManifest


def test_writes_manifest_with_required_fields(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    (spec_dir / "Demo.md").write_text("# Demo\n")
    target = RunManifest().write(
        run_dir=tmp_path,
        models={"architect": "sonnet-4-6", "icp": "haiku-4-5"},
        spec_dirs=[spec_dir],
        replicate_id=1,
    )
    assert target.exists()
    data = json.loads(target.read_text())
    assert data["models"]["icp"] == "haiku-4-5"
    assert data["replicate_id"] == 1
    assert "timestamp_utc" in data
    assert "spec_hashes" in data
    assert "Demo.md" in data["spec_hashes"]


def test_missing_spec_dir_does_not_crash(tmp_path: Path) -> None:
    target = RunManifest().write(
        run_dir=tmp_path,
        models={},
        spec_dirs=[tmp_path / "nonexistent"],
        replicate_id=0,
    )
    data = json.loads(target.read_text())
    assert data["spec_hashes"] == {}
