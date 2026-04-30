"""H5b: MCDA registry entries for the seven new categories."""

from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.mcda_registry import MCDARegistry

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCORES_ROOT = _REPO_ROOT / "eval" / "mcda_scores"


@pytest.mark.parametrize("category, expected_techs", [
    ("rest_server_handler", {"fastapi", "flask", "starlette"}),
    ("grpc_client", {"grpcio", "betterproto", "grpcio_async"}),
    ("grpc_server_handler", {"grpcio", "betterproto", "grpcio_aio"}),
    ("websocket_server_handler", {"fastapi", "websockets", "starlette"}),
    ("observability_logger", {"structlog", "loguru", "stdlib"}),
    ("secrets_provider", {"aws_secrets_manager", "azure_key_vault", "env"}),
    ("search", {"elasticsearch", "opensearch", "meilisearch"}),
])
def test_h5b_category_loads_three_candidates(
    category: str, expected_techs: set[str],
) -> None:
    candidates = MCDARegistry(_SCORES_ROOT).candidates(category)
    techs = {c.technology for c in candidates}
    assert techs == expected_techs
    assert len(candidates) == 3
    for c in candidates:
        for crit in (
            "ops", "cost", "cold", "thru", "eco", "reg", "lic", "team",
        ):
            assert 1 <= c.scores[crit] <= 5
        assert c.stability in {"ga", "beta"}
