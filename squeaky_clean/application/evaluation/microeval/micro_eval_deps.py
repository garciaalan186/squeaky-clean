"""MicroEvalDeps: collaborators injected into the MicroEvalRunner (R5.4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from squeaky_clean.application.generation.emission.implement_class import ImplementClass
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler


@dataclass(frozen=True)
class MicroEvalDeps:
    """Everything a micro-eval cell needs, built at the composition root.

    ``implementers`` and ``compilers`` map TargetLanguage.value -> adapter;
    ImplementClass is language-specific (parser + Java's ICP-tier model
    promotion), so one instance per language. Languages without an entry
    fail the cell loudly rather than silently skipping. ``extra_files``
    maps language -> static scaffold files (e.g. TypeScript's
    tsconfig.json) written into each cell dir before compiling.
    """

    implementers: dict[str, ImplementClass]
    compilers: dict[str, ProjectCompiler]
    out_root: Path
    extra_files: dict[str, dict[str, str]] = field(default_factory=dict)
