"""DSPy wrapper for the EntityICP agent (milestone D1 proof-of-concept).

Wraps the hand-written EntityICP behaviour as a `dspy.Module` so MIPROv2 /
BootstrapFewShot can optimise the prompt. The module talks to Anthropic
directly via DSPy's own LM interface; it does NOT reuse the framework's
LLMGateway. See `eval/per_agent/optimize_entity_icp.py` for the harness.
"""

from __future__ import annotations

import os
from typing import Any

import dspy

_MODEL: str = "anthropic/claude-haiku-4-5-20251001"
_TEMPERATURE: float = 0.0
_MAX_TOKENS: int = 2000


def configure_lm(model: str = _MODEL) -> None:
    """Configure DSPy's global LM. Idempotent; safe to call repeatedly."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    dspy.configure(
        lm=dspy.LM(
            model=model,
            api_key=api_key,
            temperature=_TEMPERATURE,
            max_tokens=_MAX_TOKENS,
        ),
    )


class EntityICPSignature(dspy.Signature):
    """Generate one Python Entity dataclass file from a ClassSpec.

    Output rules (condensed from EntityICP.md):
    1. Output is exactly ONE python fenced block (```python ... ```), no
       prose outside the fence.
    2. First import is `from __future__ import annotations`.
    3. Use `from dataclasses import dataclass, field` and stdlib only.
    4. Declare exactly one `@dataclass(eq=False)` class whose name matches
       the spec's `name` field.
    5. Use the spec's `fields` list verbatim (names AND types).
    6. Implement every method in `methods` with full type annotations.
    7. Override `__eq__` and `__hash__` to compare by `id` only.
    8. Raise `ValueError` for construction invariants in `__post_init__`.
       Lifecycle invariants ("X starts as Y") become field defaults — do
       NOT raise. Method-level invariants raise inside the method.
    9. mypy --strict compliant: no `Any`, no `type: ignore`.
    10. File <=80 lines, <=5 public methods, <=2 args per method.
    11. Imports for siblings come from `sibling_interfaces` (use
        `from <file> import <ClassName>` verbatim).
    """

    class_spec: str = dspy.InputField(
        desc="serialized ClassSpec — name, pattern, fields, methods, "
        "depends, concretes, invariants",
    )
    sibling_interfaces: str = dspy.InputField(
        desc="SIBLING_INTERFACES block listing each dependency class's "
        "fields, methods, invariants and dotted file path",
    )
    target_file: str = dspy.InputField(
        desc="dotted path of the file being emitted (e.g. "
        "src.domain.payments.money)",
    )
    code: str = dspy.OutputField(
        desc="ONE python fenced block (```python ... ```) containing the "
        "entire file body. No prose outside the fence.",
    )


class EntityICPModule(dspy.Module):
    """DSPy module that generates a single Entity dataclass file."""

    def __init__(self) -> None:
        super().__init__()
        self.predictor = dspy.ChainOfThought(EntityICPSignature)

    def forward(
        self,
        class_spec: str,
        sibling_interfaces: str,
        target_file: str,
    ) -> Any:  # type: ignore[explicit-any]
        return self.predictor(
            class_spec=class_spec,
            sibling_interfaces=sibling_interfaces,
            target_file=target_file,
        )
