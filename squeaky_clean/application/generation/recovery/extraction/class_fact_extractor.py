"""ClassFactExtractor: build one ClassRecord from a class AST node."""

import ast

from squeaky_clean.application.generation.recovery.extraction.class_field_extractor import (
    ClassFieldExtractor,
)
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord


class ClassFactExtractor:
    """Assembles a ClassRecord from one ``ast.ClassDef`` and file imports.

    Bases are rendered via ``ast.unparse``. ``decorators`` gathers both the
    class's own decorators and every method-level decorator (Python route
    decorators like ``@app.route`` sit on methods, and they are the INTERFACE
    signal Stage 2 keys on). Public methods (not underscore-prefixed) become
    ``name(arg, arg)`` signatures with ``self`` dropped. Fields come from
    ClassFieldExtractor. Pure — no I/O, no LLM — reproducible by construction.
    """

    def __init__(self, imports: tuple[str, ...] = ()) -> None:
        """``imports`` is the enclosing file's import list — per-extractor
        state, attached verbatim to every record it produces."""
        self._imports: tuple[str, ...] = imports
        self._fields: ClassFieldExtractor = ClassFieldExtractor()

    def record(self, node: ast.ClassDef, fqn: str) -> ClassRecord:
        """Return the ClassRecord for one class given its FQN."""
        return ClassRecord(
            fqn=fqn,
            bases=tuple(ast.unparse(b) for b in node.bases),
            methods=self._methods(node),
            fields=self._fields.extract(node),
            imports=self._imports,
            decorators=self._decorators(node),
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

    def _decorators(self, node: ast.ClassDef) -> tuple[str, ...]:
        out = [ast.unparse(d) for d in node.decorator_list]
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.extend(ast.unparse(d) for d in stmt.decorator_list)
        return tuple(out)
