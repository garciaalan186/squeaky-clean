"""Tests for ModelId catalog (R2.6)."""

from squeaky_clean.infrastructure.llm.model_catalog import ModelId


def test_current_model_ids_are_the_latest_generation() -> None:
    assert ModelId.OPUS == "claude-opus-4-8"
    assert ModelId.SONNET == "claude-sonnet-5"
    assert ModelId.HAIKU == "claude-haiku-4-5-20251001"


def test_all_ids_are_unique_nonempty_strings() -> None:
    ids = [
        v for k, v in vars(ModelId).items()
        if not k.startswith("_") and isinstance(v, str)
    ]
    assert ids, "ModelId should expose model-id constants"
    assert all(i.startswith("claude-") for i in ids)
    assert len(set(ids)) == len(ids)  # no duplicate strings
