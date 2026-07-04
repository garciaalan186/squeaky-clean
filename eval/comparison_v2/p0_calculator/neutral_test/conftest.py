"""Symmetric adapter for the P0 Calculator neutral test suite.

Walks the generated project's `src/` tree, imports every module, and finds
the four arithmetic operations either as (a) methods on a single class with
all four named, (b) methods on per-operation classes, or (c) module-level
free functions. The fixture returns a dict {add, subtract, multiply, divide}
of callables taking (a, b) and returning the result. Same fixture works for
Squeaky's Clean-Architecture layout and Opus's flat layouts.
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_CANDIDATES = ("src",)
OP_ALIASES: dict[str, tuple[str, ...]] = {
    "add": ("add", "plus", "sum"),
    "subtract": ("subtract", "sub", "minus"),
    "multiply": ("multiply", "mul", "times", "product"),
    "divide": ("divide", "div", "quotient"),
}


def _import_modules() -> list[Any]:
    src_roots = [PROJECT_ROOT / d for d in SRC_CANDIDATES if (PROJECT_ROOT / d).is_dir()]
    if not src_roots:
        src_roots = [PROJECT_ROOT]
    for root in src_roots:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    modules: list[Any] = []
    seen: set[Path] = set()
    for root in src_roots:
        for py in root.rglob("*.py"):
            if py in seen:
                continue
            if py.name == "__init__.py" or "__pycache__" in py.parts:
                continue
            if any(part in {"tests", "test", "neutral_test"} for part in py.parts):
                continue
            if py.name.startswith("test_"):
                continue
            seen.add(py)
            mod_name = f"_v2_p0_{py.stem}_{abs(hash(str(py))) % 1_000_000}"
            spec = importlib.util.spec_from_file_location(mod_name, py)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception:
                continue
            modules.append(module)
    return modules


def _instantiate(cls: type) -> Any | None:
    try:
        return cls()
    except TypeError:
        pass
    try:
        sig = inspect.signature(cls)
        kwargs = {}
        for name, p in sig.parameters.items():
            if p.default is not inspect.Parameter.empty:
                continue
            if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            return None
        return cls(**kwargs)
    except Exception:
        return None


def _binary_callable(fn: Callable[..., Any]) -> Callable[..., Any] | None:
    try:
        sig = inspect.signature(fn)
    except (ValueError, TypeError):
        return None
    params = [p for p in sig.parameters.values() if p.kind not in (
        inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD
    )]
    required = [p for p in params if p.default is inspect.Parameter.empty]
    if 2 <= len(required) <= 3 or (len(required) == 0 and len(params) >= 2):
        return fn
    if len(required) == 1 and len(params) >= 2:
        return fn
    return None


def _find_op(modules: list[Any], aliases: tuple[str, ...]) -> Callable[..., Any]:
    # 1. Method on a class
    for module in modules:
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if getattr(cls, "__module__", None) != module.__name__:
                continue
            for alias in aliases:
                method = getattr(cls, alias, None)
                if not callable(method):
                    continue
                instance = _instantiate(cls)
                if instance is None:
                    continue
                bound = getattr(instance, alias)
                ok = _binary_callable(bound)
                if ok is not None:
                    return ok
    # 2. Module-level free function
    for module in modules:
        for alias in aliases:
            fn = getattr(module, alias, None)
            if not callable(fn) or inspect.isclass(fn):
                continue
            ok = _binary_callable(fn)
            if ok is not None:
                return ok
    raise LookupError(f"No callable found among aliases {aliases!r}")


class _LazyOps:
    def __init__(self, modules: list[Any]) -> None:
        self._modules = modules
        self._resolved: dict[str, Callable[..., Any]] = {}

    def __getitem__(self, op: str) -> Callable[..., Any]:
        if op in self._resolved:
            return self._resolved[op]
        aliases = OP_ALIASES[op]
        fn = _find_op(self._modules, aliases)  # raises LookupError per-op
        self._resolved[op] = fn
        return fn


@pytest.fixture(scope="session")
def calc() -> _LazyOps:
    return _LazyOps(_import_modules())
