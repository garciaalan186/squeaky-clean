"""Pure-Python scorer for BlobStorageAdapterICP outputs (milestone H1).

`score_blob_storage_output(spec, code, tech_spec)` returns a 0.0-1.0 score:
  0.20 valid Python AST
  0.15 mypy --strict clean (with port stub)
  0.10 class name matches spec.name
  0.20 all declared port methods are implemented
  0.15 imports resolve (only TechSpec-declared + port import)
  0.15 declared error types are caught + re-raised consistently
  0.05 file <=80 lines, <=3 public methods
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
    "BLOB_ICP_MYPY", str(Path(sys.executable).parent / "mypy"),
)
_FENCE = re.compile(r"```[A-Za-z0-9_+-]*\s*\n(?P<body>.*?)```", re.DOTALL)
_WEIGHTS = {
    "ast": 0.20, "mypy": 0.15, "name": 0.10, "methods": 0.20,
    "imports": 0.15, "errors": 0.15, "size": 0.05,
}


@dataclass
class BlobAdapterSpec:
    name: str
    methods: list[str]            # ["put_blob", "get_blob", ...]
    port_dotted: str              # "src.domain.storage.blob_store"
    port_class: str               # "BlobStore"
    primary_imports: list[str]    # raw import lines from TechSpec
    error_types: list[str]        # union of all primary_operations[*].error_types


def extract_code(raw: str) -> str:
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
    return [
        n.name for n in cls.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not n.name.startswith("_")
    ]


def _all_methods_implemented(cls: ast.ClassDef, declared: list[str]) -> bool:
    pub = set(_public_methods(cls))
    return all(m in pub for m in declared)


def _imports_clean(tree: ast.Module, allowed_modules: set[str]) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in allowed_modules:
                    return False
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                return False
            if node.module is None:
                return False
            top = node.module.split(".")[0]
            if top not in allowed_modules:
                return False
    return True


def _errors_handled(cls: ast.ClassDef, errors: set[str]) -> bool:
    """Every public method has at least one try/except catching declared errors."""
    if not errors:
        return True
    seen_method_with_handler = 0
    total_methods = 0
    for node in cls.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        total_methods += 1
        for sub in ast.walk(node):
            if isinstance(sub, ast.Try):
                for handler in sub.handlers:
                    caught = _names_in(handler.type)
                    if caught & errors:
                        seen_method_with_handler += 1
                        break
                else:
                    continue
                break
    return total_methods > 0 and seen_method_with_handler == total_methods


def _names_in(node: ast.expr | None) -> set[str]:
    if node is None:
        return set()
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, ast.Tuple):
        out: set[str] = set()
        for elt in node.elts:
            out |= _names_in(elt)
        return out
    return set()


def _run_mypy(code: str, port_dotted: str, port_class: str) -> bool:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "candidate.py"
        target.write_text(code)
        parts = port_dotted.split(".")
        cur = root
        for part in parts[:-1]:
            cur = cur / part
            cur.mkdir(exist_ok=True)
            (cur / "__init__.py").touch()
        stub = cur / f"{parts[-1]}.py"
        stub.write_text(
            "from __future__ import annotations\n"
            f"class {port_class}:\n"
            "    def __init__(self, *args: object, **kwargs: object) -> None: ...\n"
            "    def put_blob(self, key: str, body: bytes) -> None: ...\n"
            "    def get_blob(self, key: str) -> bytes:\n"
            "        return b\"\"\n"
            "    def delete_blob(self, key: str) -> None: ...\n"
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


def _allowed_modules(spec: BlobAdapterSpec) -> set[str]:
    out = {"__future__"}
    for line in spec.primary_imports:
        toks = line.replace(",", " ").split()
        if "import" in toks:
            i = toks.index("import")
            if toks[0] == "from" and i >= 2:
                out.add(toks[1].split(".")[0])
            else:
                for name in toks[i + 1:]:
                    out.add(name.split(".")[0])
    out.add(spec.port_dotted.split(".")[0])
    return out


def score_blob_storage_output(
    spec: BlobAdapterSpec, code: str,
) -> dict[str, float | bool]:
    body = extract_code(code)
    tree = _parse(body)
    ast_ok = tree is not None
    cls = _find_class(tree, spec.name) if tree else None
    name_ok = cls is not None
    methods_ok = bool(cls and _all_methods_implemented(cls, spec.methods))
    imports_ok = bool(tree and _imports_clean(tree, _allowed_modules(spec)))
    errors_ok = bool(cls and _errors_handled(cls, set(spec.error_types)))
    size_ok = (
        len(body.splitlines()) <= 80
        and bool(cls) and len(_public_methods(cls)) <= 3
    )
    mypy_ok = ast_ok and _run_mypy(body, spec.port_dotted, spec.port_class)
    parts = {
        "ast": ast_ok, "mypy": mypy_ok, "name": name_ok,
        "methods": methods_ok, "imports": imports_ok,
        "errors": errors_ok, "size": size_ok,
    }
    total = sum(_WEIGHTS[k] * (1.0 if v else 0.0) for k, v in parts.items())
    out: dict[str, float | bool] = dict(parts)
    out["total"] = round(total, 4)
    return out
