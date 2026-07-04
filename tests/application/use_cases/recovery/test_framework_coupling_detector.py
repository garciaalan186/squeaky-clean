"""Tests for FrameworkCouplingDetector and RefactorProposalRenderer."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.framework_coupling_detector import (
    FrameworkCouplingDetector,
)
from squeaky_clean.application.use_cases.recovery.refactor_proposal_renderer import (
    RefactorProposalRenderer,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _rec(name: str, bases: tuple[str, ...]) -> ClassRecord:
    return ClassRecord(
        fqn=f"app.{name}", bases=bases, methods=(), fields=(),
        imports=(), decorators=(),
    )


_MODEL = _rec("Page", ("models.Model",))          # foreign base -> flagged
_ERROR = _rec("BadThing", ("Exception",))          # stdlib base -> not flagged
_PLAIN = _rec("Money", ())                          # no base -> not flagged
_BASE = _rec("Base", ())                            # a sibling base class
_LOCAL = _rec("Order", ("Base",))                   # sibling base -> not flagged
_CATALOG = ClassCatalog(
    classes=(_MODEL, _ERROR, _PLAIN, _BASE, _LOCAL),
    import_graph={r.fqn: () for r in (_MODEL, _ERROR, _PLAIN, _BASE, _LOCAL)},
)
_ALL_DOMAIN = {r.fqn: LayerType.DOMAIN for r in _CATALOG.classes}


def _proposals() -> tuple[object, ...]:
    return FrameworkCouplingDetector().detect_all(_CATALOG, _ALL_DOMAIN)


def test_flags_domain_class_with_foreign_base() -> None:
    fqns = {p.fqn for p in _proposals()}  # type: ignore[attr-defined]
    assert fqns == {"app.Page"}


def test_proposal_names_the_clean_split() -> None:
    proposal = _proposals()[0]
    assert proposal.entity == "Page"  # type: ignore[attr-defined]
    assert proposal.repository == "PageRepository"  # type: ignore[attr-defined]
    assert proposal.adapter == "PageAdapter"  # type: ignore[attr-defined]
    assert proposal.foreign_base == "models.Model"  # type: ignore[attr-defined]


def test_stdlib_and_sibling_bases_are_not_flagged() -> None:
    fqns = {p.fqn for p in _proposals()}  # type: ignore[attr-defined]
    assert "app.BadThing" not in fqns
    assert "app.Order" not in fqns


def test_non_domain_class_is_never_flagged() -> None:
    layers = dict(_ALL_DOMAIN)
    layers[_MODEL.fqn] = LayerType.INFRASTRUCTURE
    assert FrameworkCouplingDetector().detect_all(_CATALOG, layers) == ()


def test_renderer_reports_none_explicitly() -> None:
    assert "None" in RefactorProposalRenderer().render(())


def test_renderer_lists_each_proposal() -> None:
    text = RefactorProposalRenderer().render(_proposals())  # type: ignore[arg-type]
    assert "app.Page" in text
    assert "PageRepository" in text
    assert "Entity" in text
