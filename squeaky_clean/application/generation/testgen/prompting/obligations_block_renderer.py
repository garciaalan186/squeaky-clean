"""ObligationsBlockRenderer: the TestObligations section of the prompt."""

from squeaky_clean.application.generation.testgen.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


class ObligationsBlockRenderer:
    """Renders the contract block a module must discharge (rec 2/3/4/5)."""

    def render(self, ctx: TestArchitectureContext) -> list[str]:
        """The contract this module must discharge (rec 2/3/4/5).

        Infrastructure modules are integration-only (no unit tests). Other
        modules emit ONE test per projected obligation targeting one of their
        classes — narrowing generation to contract-bearing subjects and
        carrying the source criterion for traceability.
        """
        module = ctx.module
        if module.layer is LayerType.INFRASTRUCTURE:
            return ["Integration: this module's adapters require live "
                    "infrastructure. Emit ZERO tests here — the developer "
                    "owns integration tests for these classes."]
        if ctx.architecture is None:
            return []
        names = {c.name for c in module.classes}
        # Constructor-invariant duties are emitted deterministically elsewhere
        # (EmitInvariantTests); the LLM only writes behavioural criterion tests.
        mine = [o for o in ProjectTestObligations().project(
            ctx.architecture, ctx.problem)
            if o.target_class in names and o.method != "<init>"]
        if not mine:
            return []
        out = ["TestObligations (emit EXACTLY one test per line and ONLY "
               "these — do NOT add field-storage or happy-path tests; comment "
               "each test with its `from:` source):"]
        for o in mine:
            out.append(
                f"  - {o.target_class}.{o.method} must {o.kind.value} "
                f"({o.detail or 'the declared outcome'}) — from: {o.source}")
        return out
