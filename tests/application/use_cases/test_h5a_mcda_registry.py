"""H5a: MCDA registry entries for the five new categories."""

from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.mcda_registry import MCDARegistry

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCORES_ROOT = _REPO_ROOT / "eval" / "mcda_scores"


@pytest.mark.parametrize("category, expected_techs", [
    ("relational_db", {"sqlite", "postgres", "mysql"}),
    ("document_db", {"mongodb", "dynamodb", "cosmos"}),
    ("message_queue_producer", {"kafka", "rabbitmq", "sqs"}),
    ("message_queue_consumer", {"kafka", "rabbitmq", "sqs"}),
    ("stream_processor", {"kafka_streams", "flink", "beam"}),
])
def test_h5a_category_loads_three_candidates(
    category: str, expected_techs: set[str],
) -> None:
    candidates = MCDARegistry(_SCORES_ROOT).candidates(category)
    techs = {c.technology for c in candidates}
    assert techs == expected_techs
    assert len(candidates) == 3
    for c in candidates:
        for crit in ("ops", "cost", "cold", "thru", "eco", "reg", "lic", "team"):
            assert 1 <= c.scores[crit] <= 5
        assert c.stability == "ga"
