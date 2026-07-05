"""Full-spine test: ingest -> layers -> decompose -> emit -> parse -> validate."""

from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.recovery.layer_assigner import LayerAssigner
from squeaky_clean.application.use_cases.recovery.module_decomposer import ModuleDecomposer
from squeaky_clean.application.use_cases.recovery.pattern_classifier import PatternClassifier
from squeaky_clean.application.use_cases.recovery.python_class_catalog_extractor import (
    PythonClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.squib_emitter import SquibEmitter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_FILES = {
    "shop/__init__.py": "",
    "shop/domain/__init__.py": "",
    "shop/domain/line_item.py": (
        "from dataclasses import dataclass\n\n\n"
        "@dataclass\nclass LineItem:\n    sku: str\n\n"
        "    def subtotal(self) -> int:\n        return 0\n"
    ),
    "shop/domain/order.py": (
        "from dataclasses import dataclass\n"
        "from shop.domain.line_item import LineItem\n\n\n"
        "@dataclass\nclass Order:\n    id: str\n\n"
        "    def total(self, item: LineItem) -> int:\n        return 0\n"
    ),
    "shop/infra/__init__.py": "",
    "shop/infra/order_repo.py": (
        "from shop.domain.order import Order\n\n\n"
        "class OrderRepo:\n"
        "    def save(self, order: Order) -> None:\n        self._last = order\n\n"
        "    def find_by_id(self, key: str) -> object:\n        return self._last\n"
    ),
    "shop/app/__init__.py": "",
    "shop/app/order_service.py": (
        "from shop.domain.order import Order\n"
        "from shop.infra.order_repo import OrderRepo\n\n\n"
        "class OrderService:\n"
        "    def place(self, order: Order) -> None:\n        self._repo = OrderRepo()\n"
    ),
    "shop/api/__init__.py": "",
    "shop/api/order_controller.py": (
        "from shop.app.order_service import OrderService\n\n"
        "app = object()\n\n\n"
        "class OrderController:\n"
        "    @app.route('/orders')\n"
        "    def list_orders(self, request: str) -> str:\n        return ''\n"
    ),
}


def _ingest(tmp: Path) -> tuple[ClassCatalog, dict[str, LayerType]]:
    for rel, body in _FILES.items():
        path = tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    catalog = PythonClassCatalogExtractor().extract(tmp)
    return catalog, LayerAssigner().assign(catalog)


def _spec(tmp: Path) -> ArchitectureSpec:
    catalog, layers = _ingest(tmp)
    return ModuleDecomposer().decompose(catalog, layers)


def _module(spec: ArchitectureSpec, name: str) -> object:
    return next(m for m in spec.modules if m.name == name)


def test_decomposed_spec_validates_clean(tmp_path: Path) -> None:
    assert _spec(tmp_path).validate() == ()


def test_domain_scc_seeds_domain_modules(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    order = _module(spec, "Order")
    assert order.layer is LayerType.DOMAIN  # type: ignore[attr-defined]


def test_infra_and_app_attach_to_domain_module(tmp_path: Path) -> None:
    order = _module(_spec(tmp_path), "Order")
    names = {c.name for c in order.classes}  # type: ignore[attr-defined]
    assert {"Order", "OrderRepo", "OrderService"} <= names


def test_controller_routes_to_its_own_interface_module(tmp_path: Path) -> None:
    ctl = _module(_spec(tmp_path), "OrderController")
    assert ctl.layer is LayerType.INTERFACE  # type: ignore[attr-defined]


def test_emitted_squib_round_trips_and_validates(tmp_path: Path) -> None:
    spec = _spec(tmp_path)
    reparsed = ParseArchitectureNotation().parse(SquibEmitter().emit(spec))
    assert reparsed.modules == spec.modules
    assert reparsed.validate() == ()


def test_classified_patterns_thread_into_specs(tmp_path: Path) -> None:
    catalog, layers = _ingest(tmp_path)
    patterns = PatternClassifier().classify_all(catalog, layers)
    spec = ModuleDecomposer().decompose(catalog, layers, patterns)
    by_name = {c.name: c.pattern for m in spec.modules for c in m.classes}
    assert by_name["Order"] == "Entity"
    assert by_name["LineItem"] == "ValueObject"
    assert by_name["OrderRepo"] == "Repository"
    assert by_name["OrderService"] == "UseCase"
    assert spec.validate() == ()
