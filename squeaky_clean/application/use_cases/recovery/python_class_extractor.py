"""PythonClassExtractor: turn one parsed module into ClassRecords."""

import ast

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.class_fact_extractor import (
    ClassFactExtractor,
)


class PythonClassExtractor:
    """Extracts every top-level class in one module as ClassRecords.

    File-level ``import x`` and ``from m import n`` statements are
    collected once and attached to each class as candidate dependency
    targets (``m.n`` form for from-imports). Each class FQN is the module
    prefix plus the class name. Nested/inner classes are ignored — only
    ``module.body`` ClassDefs are catalogued.
    """

    def __init__(self) -> None:
        self._facts: ClassFactExtractor = ClassFactExtractor()

    def extract(self, module: ast.Module, prefix: str) -> tuple[ClassRecord, ...]:
        """Return ClassRecords for every top-level class in the module."""
        imports = self._imports(module)
        out: list[ClassRecord] = []
        for stmt in module.body:
            if isinstance(stmt, ast.ClassDef):
                fqn = f"{prefix}.{stmt.name}"
                out.append(self._facts.record(stmt, fqn, imports))
        return tuple(out)

    def _imports(self, module: ast.Module) -> tuple[str, ...]:
        out: list[str] = []
        for stmt in module.body:
            if isinstance(stmt, ast.Import):
                out.extend(alias.name for alias in stmt.names)
            elif isinstance(stmt, ast.ImportFrom) and stmt.module:
                out.extend(f"{stmt.module}.{alias.name}" for alias in stmt.names)
        return tuple(out)
