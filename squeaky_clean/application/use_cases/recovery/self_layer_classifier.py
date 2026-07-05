"""SelfLayerClassifier: layer a class from its own AST signals alone."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType

_INTERFACE_MARKERS: frozenset[str] = frozenset({
    "route", "get", "post", "put", "delete", "patch",
    "websocket", "api_route", "endpoint", "controller", "restcontroller",
})


class SelfLayerClassifier:
    """Assigns a provisional layer from a class's decorators and methods.

    A framework entry-point decorator (``@app.route``, ``@RestController``,
    ``@router.get``) routes to INTERFACE. Otherwise, method verbs matching
    an infrastructure category via ``infer_category`` route to
    INFRASTRUCTURE. Everything else is provisionally DOMAIN; the caller
    promotes orchestrators to APPLICATION in a second pass.
    """

    def classify(self, record: ClassRecord) -> LayerType:
        """Return INTERFACE, INFRASTRUCTURE, or provisional DOMAIN."""
        if any(self._marker(d) in _INTERFACE_MARKERS for d in record.decorators):
            return LayerType.INTERFACE
        verbs = tuple(m.split("(", 1)[0] for m in record.methods)
        if infer_category(verbs) is not None:
            return LayerType.INFRASTRUCTURE
        return LayerType.DOMAIN

    def _marker(self, decorator: str) -> str:
        head = decorator.split("(", 1)[0]
        return head.rsplit(".", 1)[-1].strip().lower()
