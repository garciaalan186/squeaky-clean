"""Symmetric adapter for the P3 Chat App neutral test suite.

The chat domain has 5 operations: create_user, create_room, join_room,
send_message, get_history. Plus per-entity attributes: user.name,
room.name, room.member_count, room.message_count.

The adapter searches the generated `src/` tree for any of these in three
shapes: (a) module-level free functions, (b) methods on a service class,
(c) methods on the relevant entity (e.g. `room.send_message(user, content)`).
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

CREATE_USER_NAMES = ("create_user", "register_user", "add_user", "new_user")
CREATE_ROOM_NAMES = ("create_room", "new_room", "make_room", "add_room")
JOIN_ROOM_NAMES = ("join_room", "join", "add_member")
SEND_MESSAGE_NAMES = ("send_message", "post_message", "send", "post")
GET_HISTORY_NAMES = ("get_history", "history", "list_messages", "messages")

NAME_ATTRS = ("name", "username", "title")
MEMBER_COUNT_ATTRS = ("member_count", "members_count", "num_members")
MESSAGE_COUNT_ATTRS = ("message_count", "messages_count", "num_messages")


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
            if py in seen or py.name == "__init__.py" or "__pycache__" in py.parts:
                continue
            if any(part in {"tests", "test", "neutral_test"} for part in py.parts):
                continue
            if py.name.startswith("test_"):
                continue
            seen.add(py)
            mod_name = f"_v2_p3_{py.stem}_{abs(hash(str(py))) % 1_000_000}"
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
    if any(p.default is inspect.Parameter.empty and p.kind not in (
            inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD,
        ) for p in sig.parameters.values()):
        return None
    try:
        return cls()
    except Exception:
        return None


def _find_callable(
    modules: list[Any], classes: list[type], names: tuple[str, ...],
    instance_cache: dict[type, Any],
) -> Callable[..., Any] | None:
    """Search free functions, then class methods, for first match."""
    for module in modules:
        for name in names:
            fn = getattr(module, name, None)
            if callable(fn) and not inspect.isclass(fn):
                return fn
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


def _read_attr(obj: Any, candidates: tuple[str, ...]) -> Any:
    for attr in candidates:
        val = getattr(obj, attr, None)
        if val is not None:
            return val() if callable(val) else val
    raise AttributeError(f"{obj!r} has none of attrs {candidates!r}")


class _ChatOps:
    def __init__(self, modules: list[Any]) -> None:
        self._modules = modules
        self._classes = _all_classes(modules)
        self._instance_cache: dict[type, Any] = {}

    def create_user(self, name: str) -> Any:
        fn = _find_callable(self._modules, self._classes, CREATE_USER_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no create_user found")
        return fn(name)

    def create_room(self, name: str) -> Any:
        fn = _find_callable(self._modules, self._classes, CREATE_ROOM_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no create_room found")
        return fn(name)

    def join_room(self, user: Any, room: Any) -> Any:
        # Try room.join(user) first (most natural OO shape)
        for name in JOIN_ROOM_NAMES:
            method = getattr(room, name, None)
            if callable(method):
                try:
                    return method(user) or room
                except TypeError:
                    continue
        # Else search free fn / service method
        fn = _find_callable(self._modules, self._classes, JOIN_ROOM_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no join_room found")
        # Try (user, room) and (room, user) orderings
        for args in ((user, room), (room, user)):
            try:
                return fn(*args) or room
            except (TypeError, ValueError):
                continue
        raise LookupError("join_room found but no working arg order")

    def send_message(self, user: Any, room: Any, content: str) -> Any:
        for name in SEND_MESSAGE_NAMES:
            method = getattr(room, name, None)
            if callable(method):
                try:
                    return method(user, content)
                except TypeError:
                    try:
                        return method(content, user)
                    except TypeError:
                        continue
        fn = _find_callable(self._modules, self._classes, SEND_MESSAGE_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no send_message found")
        for args in ((user, room, content), (room, user, content), (user, content, room)):
            try:
                return fn(*args)
            except (TypeError, ValueError) as exc:
                # ValueError is the expected error path — re-raise immediately
                if isinstance(exc, ValueError):
                    raise
                continue
        raise LookupError("send_message found but no working arg order")

    def get_history(self, room: Any) -> list[Any]:
        for name in GET_HISTORY_NAMES:
            method = getattr(room, name, None)
            if callable(method):
                try:
                    return list(method())
                except TypeError:
                    continue
        fn = _find_callable(self._modules, self._classes, GET_HISTORY_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no get_history found")
        try:
            return list(fn(room))
        except TypeError:
            return list(fn())

    def name_of(self, obj: Any) -> str:
        return str(_read_attr(obj, NAME_ATTRS))

    def member_count(self, room: Any) -> int:
        return int(_read_attr(room, MEMBER_COUNT_ATTRS))

    def message_count(self, room: Any) -> int:
        return int(_read_attr(room, MESSAGE_COUNT_ATTRS))


@pytest.fixture(scope="function")
def chat() -> _ChatOps:
    return _ChatOps(_import_modules())
