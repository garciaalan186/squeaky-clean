"""Unit tests for ParseArchitectureNotation."""

import pytest

from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError

_SINGLE = """\
MODULE Cart
LAYER Domain
EXPORTS [Cart]
DEPENDS []
CLASSES {
  Cart -> SimpleClass {
    fields:     []
    methods:    []
    depends:    []
    invariants: []
  }
}
INVARIANTS []
"""

_MULTI = """\
MODULE Cart
LAYER Domain
EXPORTS [Cart]
DEPENDS [Catalog::Product]
CLASSES {
  Cart -> SimpleClass {
    fields:     []
    methods:    []
    depends:    []
    invariants: []
  }
}
INVARIANTS []

MODULE Catalog
LAYER Domain
EXPORTS [Product]
DEPENDS []
CLASSES {
  Product -> ValueObject {
    fields:     [name: str]
    methods:    []
    depends:    []
    invariants: ["name must be non-empty"]
  }
}
INVARIANTS []
"""


def test_single_module_returns_one_module_spec() -> None:
    arch = ParseArchitectureNotation().parse(_SINGLE)
    assert len(arch.modules) == 1
    assert arch.modules[0].name == "Cart"
    assert arch.graph.is_dag() is True


def test_multi_module_returns_two_with_edges() -> None:
    arch = ParseArchitectureNotation().parse(_MULTI)
    assert len(arch.modules) == 2
    names = {m.name for m in arch.modules}
    assert names == {"Cart", "Catalog"}
    assert "Catalog" in arch.graph.edges["Cart"]
    assert arch.graph.is_dag() is True
    assert arch.validate() == ()


def test_empty_text_raises() -> None:
    with pytest.raises(NotationParseError):
        ParseArchitectureNotation().parse("no module here")
