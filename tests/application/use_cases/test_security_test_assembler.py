"""Tests for SecurityTestAssembler strict-fence handling (R3.1)."""

from squeaky_clean.application.generation.security.security_concern import SecurityConcern
from squeaky_clean.application.generation.security.security_test_assembler import (
    SecurityTestAssembler,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _concern() -> SecurityConcern:
    return SecurityConcern(
        category="injection", target_class="Payment",
        description="d", test_scenario="s",
    )


def _module() -> ModuleSpec:
    payment = ClassSpec(
        name="Payment", pattern="Entity", implements=None,
        methods=(), depends=(), concretes=(),
    )
    return ModuleSpec(name="Payments", layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(payment,), invariants=())


def _resp(content: str) -> LLMResponse:
    return LLMResponse(
        content=content, input_tokens=1, output_tokens=1,
        cost_usd=0.0, duration_ms=1,
    )


def test_fenced_response_yields_one_skeleton() -> None:
    resp = _resp("```python\ndef test_x():\n    assert True\n```")
    arch = SecurityTestAssembler(module=_module()).assemble(
        (resp,), (_concern(),),
    )
    assert len(arch.test_skeletons) == 1
    assert "def test_x" in arch.test_skeletons[0].code


def test_prose_only_response_is_skipped_not_written_as_code() -> None:
    # R3.1: no fence → prose, must NOT become a .py file that breaks collection.
    resp = _resp("I could not find a concrete vulnerability to test here.")
    arch = SecurityTestAssembler(module=_module()).assemble(
        (resp,), (_concern(),),
    )
    assert arch.test_skeletons == ()
