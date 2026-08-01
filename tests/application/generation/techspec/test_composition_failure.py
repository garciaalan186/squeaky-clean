"""Tests for CompositionFailure: the rejected-composition value object."""

from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.application.generation.techspec.composition_failure import (
    CompositionFailure,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation


def _assignment() -> ClassAssignment:
    spec = ClassSpec(name="Payment", pattern="Entity", implements=None,
                     methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Payments", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(spec,), invariants=())
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    return ClassAssignment(
        class_spec=spec, module=module, toolkit=toolkit,
        emitter_spec_name="python/ddd_clean/EntityEmitter",
        file_path="src/payment.py", test_file_path="tests/test_payment.py",
    )


def _tech_spec() -> TechSpec:
    op = TechSpecOperation(name="save", signature="save(x)", sdk_call="db.save",
                           error_types=("Error",), idempotency="idempotent")
    return TechSpec(schema_version="v1", category="relational_db",
                    technology="sqlite", version_pin="3", language="python",
                    install={}, imports={}, client_construction={},
                    primary_operations=(op,), auth={})


def test_carries_assignment_spec_and_errors() -> None:
    failure = CompositionFailure(_assignment(), _tech_spec(), ("bad op",))
    assert failure.assignment.class_spec.name == "Payment"
    assert failure.tech_spec.technology == "sqlite"
    assert failure.errors == ("bad op",)


def test_is_frozen() -> None:
    failure = CompositionFailure(_assignment(), _tech_spec(), ("e",))
    try:
        failure.errors = ("x",)  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised
