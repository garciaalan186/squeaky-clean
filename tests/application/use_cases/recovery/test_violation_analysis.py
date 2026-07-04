"""Tests for the Analyze phase: ViolationAnalysis + serializer + renderer."""

import json

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport
from squeaky_clean.application.use_cases.recovery.violation_analysis import (
    ViolationAnalysis,
)
from squeaky_clean.application.use_cases.recovery.violation_report_renderer import (
    ViolationReportRenderer,
)
from squeaky_clean.application.use_cases.recovery.violation_report_serializer import (
    ViolationReportSerializer,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _record(fqn: str, bases: tuple[str, ...] = ()) -> ClassRecord:
    return ClassRecord(
        fqn=fqn, bases=bases, methods=(), fields=(), imports=(), decorators=(),
    )


def _cls(name: str, methods: tuple[str, ...] = ()) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="SimpleClass", implements=None, methods=methods,
        depends=(), concretes=(), fields=(), invariants=(),
    )


_CATALOG = ClassCatalog(
    classes=(
        _record("shop.page.Page", ("models.Model",)),
        _record("shop.order.Order"),
        _record("shop.repo.OrderRepo"),
    ),
    import_graph={
        "shop.order.Order": ("shop.repo.OrderRepo",),
        "shop.page.Page": (), "shop.repo.OrderRepo": (),
    },
)
_LAYERS = {
    "shop.page.Page": LayerType.DOMAIN,
    "shop.order.Order": LayerType.DOMAIN,
    "shop.repo.OrderRepo": LayerType.INFRASTRUCTURE,
}
_MODULE = ModuleSpec(
    name="Shop", layer=LayerType.DOMAIN, exports=(), depends=(),
    classes=(_cls("God", tuple(f"m{i}()" for i in range(6))), _cls("Empty")),
    invariants=(),
)
_ARTIFACT = RecoveryArtifact(
    catalog=_CATALOG, layers=_LAYERS,
    spec=ArchitectureSpec(
        modules=(_MODULE,),
        graph=ArchitectureGraph(edges={"Shop": ("Other",), "Other": ("Shop",)}),
    ),
)


def _report() -> ViolationReport:
    return ViolationAnalysis().analyze(_ARTIFACT)


def test_every_category_is_detected() -> None:
    assert set(_report().by_category()) == {
        "framework-coupling", "dependency-rule",
        "cyclic-dependency", "granularity", "decorative-class",
    }


def test_framework_coupling_targets_the_model() -> None:
    assert _report().by_category()["framework-coupling"][0].target == "shop.page.Page"


def test_dependency_rule_flags_domain_importing_infrastructure() -> None:
    detail = _report().by_category()["dependency-rule"][0].detail
    assert detail == "domain class imports infrastructure class"


def test_granularity_flags_the_god_class() -> None:
    assert any(v.target == "God" for v in _report().by_category()["granularity"])


def test_decorative_flags_the_empty_class() -> None:
    assert any(v.target == "Empty" for v in _report().by_category()["decorative-class"])


def test_violation_id_is_stable_category_target() -> None:
    coupling = _report().by_category()["framework-coupling"][0]
    assert coupling.violation_id == "framework-coupling:shop.page.Page"


def test_serializer_emits_ids_in_json() -> None:
    data = json.loads(ViolationReportSerializer().serialize(_report()))
    ids = {v["id"] for v in data["violations"]}
    assert "framework-coupling:shop.page.Page" in ids


def test_renderer_groups_by_category() -> None:
    text = ViolationReportRenderer().render(_report())
    assert "## framework-coupling" in text
    assert "## dependency-rule" in text


def test_renderer_reports_clean_explicitly() -> None:
    assert "None found" in ViolationReportRenderer().render(ViolationReport(()))
