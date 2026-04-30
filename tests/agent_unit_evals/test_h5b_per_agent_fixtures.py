"""H5b: per-agent fixture coverage check.

Each Tier C ICP must have at least 3 fixtures spanning at least 2
technologies. Each fixture must reference a TechSpec snapshot that exists
on disk and lists the imports / error types we expect the ICP to emit.
"""

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES_ROOT = _REPO_ROOT / "eval" / "per_agent" / "fixtures"
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"

_AGENTS = [
    "rest_server_handler_icp",
    "grpc_client_icp",
    "grpc_server_handler_icp",
    "web_socket_server_handler_icp",
    "observability_logger_icp",
    "secrets_provider_icp",
    "search_icp",
]


def _fixtures_for(agent: str) -> list[Path]:
    return sorted((_FIXTURES_ROOT / agent).glob("*.json"))


@pytest.mark.parametrize("agent", _AGENTS)
def test_each_agent_has_at_least_three_fixtures(agent: str) -> None:
    assert len(_fixtures_for(agent)) >= 3


@pytest.mark.parametrize("agent", _AGENTS)
def test_each_agent_covers_at_least_two_technologies(agent: str) -> None:
    techs = set()
    for fx in _fixtures_for(agent):
        spec_path = json.loads(fx.read_text())["tech_spec_path"]
        techs.add(spec_path.split("/")[1])
    assert len(techs) >= 2, f"{agent}: only {techs!r}"


@pytest.mark.parametrize("agent", _AGENTS)
def test_each_fixture_points_to_an_existing_techspec(agent: str) -> None:
    for fx in _fixtures_for(agent):
        spec_path = json.loads(fx.read_text())["tech_spec_path"]
        assert (_TECH_ROOT / spec_path).is_file(), (
            f"{agent}/{fx.name} references missing {spec_path}"
        )


@pytest.mark.parametrize("agent", _AGENTS)
def test_each_fixture_lists_expected_imports_and_errors(agent: str) -> None:
    for fx in _fixtures_for(agent):
        body = json.loads(fx.read_text())
        assert body["expected_imports"], f"{agent}/{fx.name}: empty imports"
        assert body["expected_error_types"], (
            f"{agent}/{fx.name}: empty error types"
        )
