"""Live integration test for Phase 4: OrchestrateModule against the real Claude CLI."""

import ast
import os
from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.implement_class import ImplementClass
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_SKIP_REASON = "Set RUN_INTEGRATION_TESTS=1 to enable live LLM calls"


def _p0_module() -> ModuleSpec:
    operand = ClassSpec(
        name="Operand",
        pattern="ValueObject",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
    )
    service = ClassSpec(
        name="CalculatorService",
        pattern="SimpleClass",
        implements=None,
        methods=(
            "add(a: Operand, b: Operand): Operand",
            "subtract(a: Operand, b: Operand): Operand",
            "divide(a: Operand, b: Operand): Operand",
        ),
        depends=("Operand",),
        concretes=(),
    )
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("CalculatorService", "Operand"),
        depends=(),
        classes=(operand, service),
        invariants=("Division by zero is an error",),
    )


@pytest.mark.integration
def test_orchestrate_module_live(tmp_path: Path) -> None:
    if os.environ.get("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip(_SKIP_REASON)
    router = ModelRouter({
        ModelTier.ARCHITECT: "claude-sonnet-4-6",
        ModelTier.MANAGER: "claude-sonnet-4-6",
        ModelTier.ICP: "claude-haiku-4-5-20251001",
    })
    gateway = ClaudeCLIGateway()
    ic = ImplementClass(gateway, router)
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    ap = AssignPatterns(toolkit, tmp_path)
    uc = OrchestrateModule(ic, ap)
    impl = uc.execute(_p0_module())
    assert len(impl.implemented_classes) == 2
    for ic_result in impl.implemented_classes:
        assert ic_result.code.strip(), f"{ic_result.class_name} code empty"
        ast.parse(ic_result.code)
        print(
            f"[phase4-live] class={ic_result.class_name} "
            f"lines={len(ic_result.code.splitlines())} "
            f"cost_usd={ic_result.cost_usd:.4f} "
            f"duration_ms={ic_result.duration_ms}"
        )
    print(
        f"[phase4-live] total cost_usd={impl.total_cost_usd:.4f} "
        f"total duration_ms={impl.total_duration_ms}"
    )
