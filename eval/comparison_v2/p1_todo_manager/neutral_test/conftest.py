"""Symmetric adapter for the P1 Todo Manager neutral test suite.

Discovers, in the generated project's `src/` tree:
  - A `create_todo(title) -> Todo` entry point (function or use-case method).
  - A `mark_complete(todo)` operation, OR a Todo with a `mark_complete()` method.
  - A `list_pending()` operation that returns pending todos.
  - Reads attributes/properties on the todo: `title`, and a pending flag named
    `is_pending` / `pending` / `completed` / `is_completed` / `done`.

Works against Squeaky's split (CreateTodoUseCase + InMemoryTodoRepository) and
flat layouts where everything lives on one TodoManager class.
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
CREATE_NAMES = ("create_todo", "create", "add_todo", "add", "new_todo", "make_todo")
MARK_COMPLETE_NAMES = ("mark_complete", "complete", "finish", "done", "mark_done", "mark_completed")
LIST_PENDING_NAMES = ("list_pending", "pending", "get_pending", "list_open", "list_active", "incomplete")
PENDING_ATTRS = ("is_pending", "pending", "is_open", "is_active")
COMPLETED_ATTRS = ("is_completed", "completed", "is_done", "done", "finished")


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
            mod_name = f"_v2_p1_{py.stem}_{abs(hash(str(py))) % 1_000_000}"
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


def _all_classes(modules: list[Any]) -> list[type]:
    out: list[type] = []
    for module in modules:
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if getattr(cls, "__module__", None) == module.__name__:
                out.append(cls)
    return out


def _try_instantiate(cls: type) -> Any | None:
    try:
        return cls()
    except TypeError:
        pass
    try:
        sig = inspect.signature(cls)
    except (ValueError, TypeError):
        return None
    args: list[Any] = []
    for p in sig.parameters.values():
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if p.default is not inspect.Parameter.empty:
            continue
        # Try to fill required deps recursively (one level deep)
        ann = p.annotation
        if inspect.isclass(ann):
            try:
                args.append(ann())
                continue
            except Exception:
                pass
        return None
    try:
        return cls(*args)
    except Exception:
        return None


def _find_function(modules: list[Any], names: tuple[str, ...]) -> Callable[..., Any] | None:
    # Module-level function with one of these names
    for module in modules:
        for name in names:
            fn = getattr(module, name, None)
            if callable(fn) and not inspect.isclass(fn):
                return fn
    return None


def _find_method(
    classes: list[type],
    names: tuple[str, ...],
    *,
    instance_cache: dict[type, Any],
) -> Callable[..., Any] | None:
    for cls in classes:
        for name in names:
            method = getattr(cls, name, None)
            if not callable(method):
                continue
            if cls not in instance_cache:
                inst = _try_instantiate(cls)
                if inst is None:
                    continue
                instance_cache[cls] = inst
            return getattr(instance_cache[cls], name)
    return None


def _read_pending_flag(todo: Any) -> bool:
    """Return True if the todo is in pending state, regardless of attribute name."""
    for attr in PENDING_ATTRS:
        val = getattr(todo, attr, None)
        if val is not None:
            return bool(val() if callable(val) else val)
    for attr in COMPLETED_ATTRS:
        val = getattr(todo, attr, None)
        if val is not None:
            return not bool(val() if callable(val) else val)
    raise AttributeError(f"todo {todo!r} has no recognizable pending/completed flag")


def _read_title(todo: Any) -> str:
    for attr in ("title", "name", "description", "text"):
        val = getattr(todo, attr, None)
        if val is not None:
            return str(val)
    raise AttributeError(f"todo {todo!r} has no recognizable title")


def _mark_complete_on(
    todo: Any,
    modules: list[Any],
    classes: list[type],
    instance_cache: dict[type, Any],
) -> Any:
    """Mark a todo complete by: instance method, free function, or class-method."""
    for name in MARK_COMPLETE_NAMES:
        method = getattr(todo, name, None)
        if callable(method):
            try:
                result = method()
                return result if result is not None else todo
            except TypeError:
                continue
    fn = _find_function(modules, MARK_COMPLETE_NAMES)
    if fn is not None:
        result = fn(todo)
        return result if result is not None else todo
    # Try a method on a class (e.g. TodoManager.mark_complete(todo)) — reuse cached instance
    for cls in classes:
        for name in MARK_COMPLETE_NAMES:
            method = getattr(cls, name, None)
            if not callable(method):
                continue
            if cls not in instance_cache:
                inst = _try_instantiate(cls)
                if inst is None:
                    continue
                instance_cache[cls] = inst
            bound = getattr(instance_cache[cls], name)
            try:
                result = bound(todo)
                return result if result is not None else todo
            except TypeError:
                continue
    raise LookupError("No mark_complete operation found")


class _TodoOps:
    def __init__(self, modules: list[Any]) -> None:
        self._modules = modules
        self._classes = _all_classes(modules)
        self._instance_cache: dict[type, Any] = {}

    def create(self, title: str) -> Any:
        fn = _find_function(self._modules, CREATE_NAMES)
        if fn is not None:
            return fn(title)
        method = _find_method(self._classes, CREATE_NAMES, instance_cache=self._instance_cache)
        if method is not None:
            return method(title)
        # Last resort: a Todo entity directly constructable with a title
        for cls in self._classes:
            if cls.__name__.lower() in {"todo", "todoitem", "task"}:
                try:
                    return cls(title=title)
                except TypeError:
                    try:
                        return cls(title)
                    except TypeError:
                        continue
        raise LookupError("No create_todo operation found")

    def mark_complete(self, todo: Any) -> Any:
        return _mark_complete_on(todo, self._modules, self._classes, self._instance_cache)

    def is_pending(self, todo: Any) -> bool:
        return _read_pending_flag(todo)

    def title(self, todo: Any) -> str:
        return _read_title(todo)

    def list_pending(self) -> list[Any]:
        # Free function?
        fn = _find_function(self._modules, LIST_PENDING_NAMES)
        if fn is not None:
            try:
                return list(fn())
            except TypeError:
                pass
        # Method on something?
        method = _find_method(self._classes, LIST_PENDING_NAMES, instance_cache=self._instance_cache)
        if method is not None:
            try:
                return list(method())
            except TypeError:
                # Maybe it takes a repository argument; fall through
                pass
        raise LookupError("No list_pending operation found")


@pytest.fixture(scope="function")
def todos() -> _TodoOps:
    return _TodoOps(_import_modules())
