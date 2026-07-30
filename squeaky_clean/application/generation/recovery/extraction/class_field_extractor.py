"""ClassFieldExtractor: pull declared fields from one class AST node."""

import ast


class ClassFieldExtractor:
    """Extracts ``name: Type`` field strings from a class definition.

    Captures two field sources deterministically: class-level annotated
    attributes (``x: int``) and ``self.<name>`` assignment targets found
    in method bodies. Annotated attributes keep their rendered type;
    self-assigned names without an annotation are emitted bare. Order of
    first appearance is preserved and duplicates are dropped.
    """

    def extract(self, node: ast.ClassDef) -> tuple[str, ...]:
        """Return ordered, de-duplicated field declarations for the class."""
        fields: dict[str, str] = {}
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields[stmt.target.id] = f"{stmt.target.id}: {ast.unparse(stmt.annotation)}"
        for attr in self._self_attrs(node):
            fields.setdefault(attr, attr)
        return tuple(fields.values())

    def _self_attrs(self, node: ast.ClassDef) -> list[str]:
        out: list[str] = []
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Attribute) or not isinstance(sub.ctx, ast.Store):
                continue
            if isinstance(sub.value, ast.Name) and sub.value.id == "self":
                out.append(sub.attr)
        return out
