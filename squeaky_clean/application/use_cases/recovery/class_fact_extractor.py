"""ClassFactExtractor: build one ClassRecord from a class AST node."""

import ast

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.class_field_extractor import (
    ClassFieldExtractor,
)


class ClassFactExtractor:
    """Assembles a ClassRecord from one ``ast.ClassDef`` and file imports.

    Bases and decorators are rendered via ``ast.unparse``. Public methods
    (not underscore-prefixed) become ``name(arg, arg)`` signatures with
    ``self`` dropped. Fields come from ClassFieldExtractor. The extraction
    is pure — no I/O and no LLM — so it is reproducible by construction.
    """

    def __init__(self) -> None:
        self._fields: ClassFieldExtractor = ClassFieldExtractor()

    def record(
        self, node: ast.ClassDef, fqn: str, imports: tuple[str, ...],
    ) -> ClassRecord:
        """Return the ClassRecord for one class given its FQN and imports."""
        return ClassRecord(
            fqn=fqn,
            bases=tuple(ast.unparse(b) for b in node.bases),
            methods=self._methods(node),
            fields=self._fields.extract(node),
            imports=imports,
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
        )

    def _methods(self, node: ast.ClassDef) -> tuple[str, ...]:
        out: list[str] = []
        for stmt in node.body:
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if stmt.name.startswith("_"):
                continue
            args = ", ".join(a.arg for a in stmt.args.args if a.arg != "self")
            out.append(f"{stmt.name}({args})")
        return tuple(out)
