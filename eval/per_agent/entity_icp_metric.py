"""Pure-Python scorer for EntityICP outputs (milestone D1).

`score_entity_output(spec, code)` returns a 0.0-1.0 weighted score:
  0.30 valid Python AST
  0.20 mypy --strict clean (with sibling stubs)
  0.15 class name matches spec.name
  0.15 fields verbatim
  0.10 __eq__ + __hash__ overridden
  0.05 from __future__ import annotations is the first import
  0.05 file <=80 lines and <=3 public methods
"""

# mypy: ignore-errors
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

_MYPY = os.environ.get(
    "ENTITY_ICP_MYPY",
    str(Path(sys.executable).parent / "mypy"),
)

_FENCE = re.compile(r"```[A-Za-z0-9_+-]*\s*\n(?P<body>.*?)```", re.DOTALL)
_WEIGHTS = {
    "ast": 0.30, "mypy": 0.20, "name": 0.15, "fields": 0.15,
    "eq_hash": 0.10, "future": 0.05, "size": 0.05,
}


@dataclass
class EntitySpec:
    name: str
    fields: list[str]
    methods: list[str]


def extract_code(raw: str) -> str:
    """Pull the first fenced block from raw output; fallback to raw."""
    m = _FENCE.search(raw or "")
    return (m.group("body").rstrip() if m else (raw or "")).strip()


def _parse(code: str) -> ast.Module | None:
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _find_class(tree: ast.Module, name: str) -> ast.ClassDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _public_methods(cls: ast.ClassDef) -> list[str]:
    out: list[str] = []
    for n in cls.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not n.name.startswith("_"):
                out.append(n.name)
    return out


def _has_eq_hash(cls: ast.ClassDef) -> bool:
    names = {n.name for n in cls.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return "__eq__" in names and "__hash__" in names


def _future_first(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.Expr)):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # docstring
            return False
        if isinstance(node, ast.ImportFrom):
            return node.module == "__future__"
    return False


def _fields_verbatim(cls: ast.ClassDef, declared: list[str]) -> bool:
    field_names = [d.split(":", 1)[0].strip() for d in declared]
    field_types = [d.split(":", 1)[1].split("=", 1)[0].strip()
                   for d in declared if ":" in d]
    found_names: list[str] = []
    found_types: list[str] = []
    for n in cls.body:
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            found_names.append(n.target.id)
            found_types.append(ast.unparse(n.annotation).strip())
    if found_names[: len(field_names)] != field_names:
        return False
    return all(ft.replace(" ", "") in fnd.replace(" ", "")
               or fnd.replace(" ", "") in ft.replace(" ", "")
               for ft, fnd in zip(field_types, found_types[: len(field_types)]))


def _run_mypy(code: str, siblings: list[tuple[str, str]]) -> bool:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "candidate.py"
        target.write_text(code)
        for class_name, dotted in siblings:
            parts = dotted.split(".") if dotted else [class_name.lower()]
            cur = root
            for part in parts[:-1]:
                cur = cur / part
                cur.mkdir(exist_ok=True)
                (cur / "__init__.py").touch()
            stub = cur / f"{parts[-1]}.py"
            stub.write_text(
                "from __future__ import annotations\n"
                f"class {class_name}:\n"
                "    def __init__(self, *args: object, **kwargs: object) -> None: ...\n",
            )
        # also stub bare-name fallback
        for class_name, _ in siblings:
            stub = root / f"{class_name.lower()}.py"
            if not stub.exists():
                stub.write_text(
                    "from __future__ import annotations\n"
                    f"class {class_name}:\n"
                    "    def __init__(self, *args: object, **kwargs: object) -> None: ...\n",
                )
        try:
            proc = subprocess.run(
                [_MYPY, "--strict", "--no-incremental",
                 "--cache-dir", str(root / ".cache"), str(target)],
                cwd=root, capture_output=True, text=True, timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        return proc.returncode == 0


def _siblings_from_text(siblings_text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    pat = re.compile(
        r"\s*([A-Z][A-Za-z0-9_]*)\s*\([^)]*file=([A-Za-z0-9_.]+)",
    )
    for line in siblings_text.splitlines():
        m = pat.match(line)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def score_entity_output(
    spec: EntitySpec, code: str, siblings_text: str = "",
) -> dict[str, float | bool]:
    """Score code body. Returns dict with per-component pass + total."""
    body = extract_code(code)
    tree = _parse(body)
    ast_ok = tree is not None
    cls = _find_class(tree, spec.name) if tree else None
    name_ok = cls is not None
    fields_ok = bool(cls and _fields_verbatim(cls, spec.fields))
    eq_ok = bool(cls and _has_eq_hash(cls))
    fut_ok = bool(tree and _future_first(tree))
    size_ok = (len(body.splitlines()) <= 80
               and bool(cls) and len(_public_methods(cls)) <= 3)
    mypy_ok = ast_ok and _run_mypy(body, _siblings_from_text(siblings_text))
    parts = {
        "ast": ast_ok, "mypy": mypy_ok, "name": name_ok, "fields": fields_ok,
        "eq_hash": eq_ok, "future": fut_ok, "size": size_ok,
    }
    total = sum(_WEIGHTS[k] * (1.0 if v else 0.0) for k, v in parts.items())
    out: dict[str, float | bool] = dict(parts)
    out["total"] = round(total, 4)
    return out
