"""Unit tests for the GitInfo port."""

import inspect

from squeaky_clean.domain.interfaces.provenance.git_info import GitInfo


def test_is_abstract() -> None:
    assert inspect.isabstract(GitInfo)
    assert "head_sha" in GitInfo.__abstractmethods__


def test_concrete_subclass_is_instantiable() -> None:
    class Fake(GitInfo):
        def head_sha(self) -> str:
            return "abc123"

    assert Fake().head_sha() == "abc123"
