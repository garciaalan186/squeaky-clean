"""Tests for QuerySemantic DTO."""

import pytest

from squeaky_clean.application.dtos.query_semantic import QuerySemantic


def test_query_semantic_accepts_known_shape() -> None:
    q = QuerySemantic(use_case="GetTimelineUseCase", shape="self_plus_followees")
    assert q.use_case == "GetTimelineUseCase"
    assert q.shape == "self_plus_followees"


def test_query_semantic_rejects_unknown_shape() -> None:
    with pytest.raises(ValueError, match="not in"):
        QuerySemantic(use_case="X", shape="bogus")


def test_query_semantic_rejects_empty_use_case() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        QuerySemantic(use_case="", shape="all_public")
