"""Unit tests for the ToolchainInfo port."""

import inspect

from squeaky_clean.domain.interfaces.provenance.toolchain_info import ToolchainInfo


def test_is_abstract() -> None:
    assert inspect.isabstract(ToolchainInfo)
    assert "versions" in ToolchainInfo.__abstractmethods__


def test_concrete_subclass_is_instantiable() -> None:
    class Fake(ToolchainInfo):
        def versions(self) -> dict[str, str]:
            return {"node": "v20.0.0"}

    assert Fake().versions() == {"node": "v20.0.0"}
