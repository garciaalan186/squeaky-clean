"""LayerAssigner: assign every catalogued class a Clean-Architecture layer."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.use_cases.recovery.self_layer_classifier import (
    SelfLayerClassifier,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


class LayerAssigner:
    """Two-pass, deterministic layer assignment over a ClassCatalog.

    Pass one classifies each class from its own signals (INTERFACE via
    framework decorators, INFRASTRUCTURE via infra method verbs, else
    DOMAIN). Pass two promotes any provisional-DOMAIN class that imports
    an INFRASTRUCTURE class to APPLICATION — it orchestrates domain plus
    infrastructure. No LLM runs; the same catalog yields the same layers.
    """

    def __init__(self) -> None:
        self._classifier: SelfLayerClassifier = SelfLayerClassifier()

    def assign(self, catalog: ClassCatalog) -> dict[str, LayerType]:
        """Return an FQN -> LayerType map for every catalogued class."""
        layers = {r.fqn: self._classifier.classify(r) for r in catalog.classes}
        infra = {fqn for fqn, la in layers.items() if la is LayerType.INFRASTRUCTURE}
        for fqn, layer in layers.items():
            if layer is LayerType.DOMAIN and self._orchestrates(fqn, catalog, infra):
                layers[fqn] = LayerType.APPLICATION
        return layers

    def _orchestrates(
        self, fqn: str, catalog: ClassCatalog, infra: set[str],
    ) -> bool:
        return any(dep in infra for dep in catalog.import_graph.get(fqn, ()))
