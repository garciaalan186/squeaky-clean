"""Unit tests for RunManifest."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.run_manifest import RunManifest
from squeaky_clean.domain.interfaces.provenance.git_info import GitInfo
from squeaky_clean.domain.interfaces.provenance.toolchain_info import ToolchainInfo


class _FakeGit(GitInfo):
    def head_sha(self) -> str:
        return "deadbeef" * 5


class _FakeToolchains(ToolchainInfo):
    def versions(self) -> dict[str, str]:
        return {"node": "v20.11.0"}


def test_writes_manifest_with_required_fields(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    (spec_dir / "Demo.md").write_text("# Demo\n")
    target = RunManifest(spec_dirs=[spec_dir], replicate_id=1).write(
        tmp_path, {"architect": "sonnet-4-6", "icp": "haiku-4-5"},
    )
    assert target.exists()
    data = json.loads(target.read_text())
    assert data["models"]["icp"] == "haiku-4-5"
    assert data["replicate_id"] == 1
    assert "timestamp_utc" in data
    assert "spec_hashes" in data
    assert "Demo.md" in data["spec_hashes"]


def test_missing_spec_dir_does_not_crash(tmp_path: Path) -> None:
    target = RunManifest(spec_dirs=[tmp_path / "nonexistent"]).write(tmp_path, {})
    data = json.loads(target.read_text())
    assert data["spec_hashes"] == {}


def test_unwired_probes_degrade_honestly(tmp_path: Path) -> None:
    target = RunManifest(spec_dirs=[]).write(tmp_path, {})
    data = json.loads(target.read_text())
    assert data["framework_sha"] == "unknown"
    assert data["toolchains"] == {}


def test_injected_ports_populate_provenance(tmp_path: Path) -> None:
    manifest = RunManifest(_FakeGit(), _FakeToolchains(), spec_dirs=[], replicate_id=2)
    target = manifest.write(tmp_path, {})
    data = json.loads(target.read_text())
    assert data["framework_sha"] == "deadbeef" * 5
    assert data["toolchains"] == {"node": "v20.11.0"}
