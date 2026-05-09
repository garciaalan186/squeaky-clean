"""H5a: presence + structure check for the 5 new Tier C agent specs."""

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_INFRA_SPECS = (
    _REPO_ROOT / "squeaky_clean" / "interface" / "agent_specs" / "icps" / "python"
    / "infrastructure"
)

_NEW_SPECS = [
    "RelationalDBRepositoryICP.md",
    "DocumentDBRepositoryICP.md",
    "MessageQueueProducerICP.md",
    "MessageQueueConsumerICP.md",
    "StreamProcessorICP.md",
]


@pytest.mark.parametrize("filename", _NEW_SPECS)
def test_h5a_agent_spec_exists(filename: str) -> None:
    assert (_INFRA_SPECS / filename).is_file()


@pytest.mark.parametrize("filename", _NEW_SPECS)
def test_h5a_agent_spec_has_required_sections(filename: str) -> None:
    body = (_INFRA_SPECS / filename).read_text()
    for section in (
        "Identity", "Model Tier", "Input Contract", "Output Contract",
        "Constraints", "Pattern Knowledge", "Failure Modes",
    ):
        assert section in body, f"{filename} missing section: {section}"


@pytest.mark.parametrize("filename", _NEW_SPECS)
def test_h5a_agent_spec_at_most_120_lines(filename: str) -> None:
    lines = (_INFRA_SPECS / filename).read_text().splitlines()
    assert len(lines) <= 120, (
        f"{filename}: {len(lines)} lines exceeds the 120-line cap"
    )
