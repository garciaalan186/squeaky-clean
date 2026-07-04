"""Tests for LayerAssigner (Stage-2 Clean-Architecture layer routing)."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.layer_assigner import LayerAssigner
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _rec(
    fqn: str,
    methods: tuple[str, ...] = (),
    decorators: tuple[str, ...] = (),
) -> ClassRecord:
    return ClassRecord(
        fqn=fqn, bases=(), methods=methods, fields=(),
        imports=(), decorators=decorators,
    )


_ENTITY = _rec("app.domain.order.Order", methods=("total()", "validate()"))
_REPO = _rec("app.infra.order_repo.OrderRepo", methods=("save(order)", "find_by_id(id)"))
_CONTROLLER = _rec("app.api.order_ctl.OrderController", decorators=("app.route('/o')",))
_SERVICE = _rec("app.svc.order_service.OrderService", methods=("place(order)",))

_GRAPH = {
    _SERVICE.fqn: (_REPO.fqn, _ENTITY.fqn),
    _ENTITY.fqn: (),
    _REPO.fqn: (),
    _CONTROLLER.fqn: (),
}
_CATALOG = ClassCatalog(
    classes=(_ENTITY, _REPO, _CONTROLLER, _SERVICE), import_graph=_GRAPH,
)


def _layers() -> dict[str, LayerType]:
    return LayerAssigner().assign(_CATALOG)


def test_plain_class_is_domain() -> None:
    assert _layers()[_ENTITY.fqn] is LayerType.DOMAIN


def test_infra_verbs_route_to_infrastructure() -> None:
    assert _layers()[_REPO.fqn] is LayerType.INFRASTRUCTURE


def test_framework_decorator_routes_to_interface() -> None:
    assert _layers()[_CONTROLLER.fqn] is LayerType.INTERFACE


def test_orchestrator_importing_infra_is_promoted_to_application() -> None:
    assert _layers()[_SERVICE.fqn] is LayerType.APPLICATION


def test_domain_importing_only_domain_stays_domain() -> None:
    line = _rec("app.domain.line.Line", methods=("subtotal()",))
    catalog = ClassCatalog(
        classes=(_ENTITY, line),
        import_graph={_ENTITY.fqn: (line.fqn,), line.fqn: ()},
    )
    assert LayerAssigner().assign(catalog)[_ENTITY.fqn] is LayerType.DOMAIN
