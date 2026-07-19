"""EmitInvariantTests: deterministically write construction-raises tests.

A validation invariant ("value must not be empty") maps to a fixed,
mechanical test: construct the class with a violating value and assert it
raises. LLM generation of this pattern proved unstable at temp=0, so it is
emitted deterministically here — always correct against the enforcing code,
always passing. Behavioural/criterion tests remain LLM-generated.
"""

from __future__ import annotations

import re

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.emit_invariant_test_renderer import (
    InvariantTestRenderer,
)
from squeaky_clean.application.use_cases.project_test_obligations import (
    ProjectTestObligations,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class EmitInvariantTests:
    """Writes one deterministic invariants test file per validation class."""

    def __init__(self) -> None:
        self._projector: ProjectTestObligations = ProjectTestObligations()

    def emit(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
        toolkit: LanguageToolkit,
    ) -> dict[str, str]:
        """Return {relative_path: file_contents} for each validation class."""
        wanted: dict[str, list[str]] = {}
        for ob in self._projector.project(arch, problem):
            if ob.method == "<init>":
                wanted.setdefault(ob.target_class, []).append(ob.detail)
        renderer = InvariantTestRenderer(toolkit)
        out: dict[str, str] = {}
        for name, invariants in wanted.items():
            found = self._find(arch, name)
            if found is None:
                continue
            cls, module = found
            rel, body = renderer.render(cls, module, tuple(invariants))
            out[rel] = body
        return out

    @staticmethod
    def _find(
        arch: ArchitectureSpec, name: str,
    ) -> tuple[ClassSpec, ModuleSpec] | None:
        for module in arch.modules:
            for cls in module.classes:
                if cls.name == name:
                    return cls, module
        return None


def constrained_field(invariant: str, fields: tuple[str, ...]) -> str | None:
    """The field name a value-invariant constrains (first field it names)."""
    low = invariant.lower()
    for entry in fields:
        fname = entry.split(":", 1)[0].strip()
        if re.search(rf"\b{re.escape(fname.lower())}\b", low):
            return fname
    return fields[0].split(":", 1)[0].strip() if fields else None
