"""Symmetric adapter for the P5 OAuth2 Server neutral test suite.

Operations: register_client, issue_code, exchange_code, refresh.
Returned entities: Client, AuthorizationCode, AccessToken (and implicitly
RefreshToken via refresh()).

The adapter searches free functions + class methods. For methods that take
mixed primitive + entity arguments (e.g. issue_code(client, redirect_uri)),
the adapter tries multiple positional orderings.
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

REGISTER_CLIENT_NAMES = ("register_client", "create_client", "add_client")
ISSUE_CODE_NAMES = ("issue_code", "issue_authorization_code", "create_code")
EXCHANGE_CODE_NAMES = ("exchange_code", "exchange", "redeem_code", "redeem")
REFRESH_NAMES = ("refresh", "refresh_token", "rotate", "rotate_token")
REVOKE_REFRESH_NAMES = ("revoke", "revoke_refresh", "revoke_token")


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
            mod_name = f"_v2_p5_{py.stem}_{abs(hash(str(py))) % 1_000_000}"
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
    except (TypeError, Exception):
        return None


def _find_callable(
    modules: list[Any], classes: list[type], names: tuple[str, ...],
    instance_cache: dict[type, Any],
) -> Callable[..., Any] | None:
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


def _try_call(fn: Callable[..., Any], *arg_orderings: tuple[Any, ...]) -> Any:
    """Try each positional ordering; return the first successful call's result.

    Re-raises domain errors (ValueError, RuntimeError, PermissionError) immediately —
    those are the failure paths the tests assert on.
    """
    last_type_err: TypeError | None = None
    for args in arg_orderings:
        try:
            return fn(*args)
        except TypeError as exc:
            last_type_err = exc
            continue
        except (ValueError, RuntimeError, PermissionError):
            raise
    if last_type_err:
        raise last_type_err
    raise LookupError("no successful arg ordering")


class _OAuthOps:
    def __init__(self, modules: list[Any]) -> None:
        self._modules = modules
        self._classes = _all_classes(modules)
        self._instance_cache: dict[type, Any] = {}

    def register_client(self, name: str, redirect_uri: str) -> Any:
        fn = _find_callable(self._modules, self._classes, REGISTER_CLIENT_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no register_client")
        return _try_call(fn, (name, redirect_uri), (redirect_uri, name))

    def issue_code(self, client: Any, redirect_uri: str) -> Any:
        fn = _find_callable(self._modules, self._classes, ISSUE_CODE_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no issue_code")
        client_id = getattr(client, "id", None) or getattr(client, "client_id", None) or client
        return _try_call(fn, (client, redirect_uri), (client_id, redirect_uri),
                         (redirect_uri, client), (redirect_uri, client_id))

    def exchange_code(self, code: Any) -> Any:
        fn = _find_callable(self._modules, self._classes, EXCHANGE_CODE_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no exchange_code")
        code_val = getattr(code, "value", None) or getattr(code, "code", None) or code
        return _try_call(fn, (code,), (code_val,))

    def refresh(self, refresh_token: Any) -> Any:
        fn = _find_callable(self._modules, self._classes, REFRESH_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no refresh")
        tok_val = getattr(refresh_token, "value", None) or refresh_token
        return _try_call(fn, (refresh_token,), (tok_val,))

    def has_revoke(self) -> bool:
        return _find_callable(
            self._modules, self._classes, REVOKE_REFRESH_NAMES, self._instance_cache,
        ) is not None

    def revoke_refresh(self, refresh_token: Any) -> None:
        fn = _find_callable(self._modules, self._classes, REVOKE_REFRESH_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no revoke API")
        tok_val = getattr(refresh_token, "value", None) or refresh_token
        _try_call(fn, (refresh_token,), (tok_val,))

    def refresh_token_from_access(self, access_token: Any) -> Any:
        """Extract the refresh token from an issued AccessToken, by best guess."""
        for attr in ("refresh_token", "refresh", "refresh_token_value"):
            rt = getattr(access_token, attr, None)
            if rt is not None:
                return rt
        return None


@pytest.fixture(scope="function")
def oauth() -> _OAuthOps:
    return _OAuthOps(_import_modules())
