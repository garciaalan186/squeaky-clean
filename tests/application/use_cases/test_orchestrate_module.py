"""Tests for OrchestrateModule use case."""

from pathlib import Path

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class _StubImplementClass(ImplementClass):
    def __init__(self) -> None:
        gateway = _NullGateway()
        super().__init__(gateway, ModelRouter())
        self.calls: list[str] = []
        self.seen_module_names: list[str] = []

    def execute(self, assignment: ClassAssignment) -> ImplementedClass:
        self.calls.append(assignment.class_spec.name)
        self.seen_module_names.append(assignment.module.name)
        return ImplementedClass(
            class_name=assignment.class_spec.name,
            file_path=assignment.file_path,
            code=f"class {assignment.class_spec.name}:\n    pass\n",
            test_code=None,
            cost_usd=0.01,
            duration_ms=100,
            input_tokens=25,
            output_tokens=10,
        )


class _NullGateway(LLMGateway):
    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content="", input_tokens=0, output_tokens=0,
                           cost_usd=0.0, duration_ms=0)


def _module() -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Operand", "CalculatorService"),
        depends=(),
        classes=(
            ClassSpec(
                name="Operand", pattern="ValueObject", implements=None,
                methods=(), depends=(), concretes=(),
            ),
            ClassSpec(
                name="CalculatorService", pattern="SimpleClass", implements=None,
                methods=(), depends=(), concretes=(),
            ),
        ),
        invariants=(),
    )


def test_orchestrate_module_dispatches_all_classes() -> None:
    stub = _StubImplementClass()
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    assigner = AssignPatterns(toolkit, Path("/tmp/p0"))
    uc = OrchestrateModule(stub, assigner)
    impl = uc.execute(_module())
    assert len(impl.implemented_classes) == 2
    assert {c.class_name for c in impl.implemented_classes} == {
        "Operand",
        "CalculatorService",
    }
    assert impl.total_cost_usd == 0.02
    assert impl.total_duration_ms == 200
    assert impl.total_input_tokens == 50
    assert impl.total_output_tokens == 20
    assert stub.seen_module_names == ["Calculator", "Calculator"]
