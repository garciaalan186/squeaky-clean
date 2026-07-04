"""Symmetric adapter for the EP-PROD Event Producer neutral test suite.

Two operations: ingest_event (local) + publish_event (calls Kafka).
The Kafka publisher is mocked via monkey-patching `confluent_kafka.Producer`
at import time so the test doesn't need a live broker.

Acceptance covers: body+headers → IngestedEvent with 4 contract fields
(id, received_at, headers, payload); empty body raises; >1MB body raises;
publish_event sends to topic 'events.raw' with those 4 JSON keys.
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_CANDIDATES = ("src",)

INGEST_NAMES = ("ingest_event", "ingest", "receive_event", "accept_event")
PUBLISH_NAMES = ("publish_event", "publish", "forward_event", "send_event")
CONTRACT_FIELDS = ("id", "received_at", "headers", "payload")


_kafka_mock_messages: list[dict[str, Any]] = []


class _MockKafkaProducer:
    """Pretends to be a confluent_kafka.Producer. Records each produce() call."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def produce(self, topic: str, value: Any = None, key: Any = None, **kwargs: Any) -> None:
        _kafka_mock_messages.append({"topic": topic, "value": value, "key": key, **kwargs})

    def flush(self, *args: Any, **kwargs: Any) -> int:
        return 0

    def poll(self, *args: Any, **kwargs: Any) -> int:
        return 0


def _install_kafka_mock() -> None:
    """Inject the mock Producer into confluent_kafka module space."""
    try:
        import confluent_kafka  # type: ignore
    except ImportError:
        # Construct a stub module so generated code's `from confluent_kafka import Producer` works
        mod = type(sys)("confluent_kafka")
        sys.modules["confluent_kafka"] = mod
        confluent_kafka = mod
    confluent_kafka.Producer = _MockKafkaProducer  # type: ignore[attr-defined]
    confluent_kafka.KafkaError = type("KafkaError", (Exception,), {})  # type: ignore[attr-defined]
    confluent_kafka.KafkaException = type("KafkaException", (Exception,), {})  # type: ignore[attr-defined]


def _import_modules() -> list[Any]:
    _install_kafka_mock()
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
            mod_name = f"_v2_ep_{py.stem}_{abs(hash(str(py))) % 1_000_000}"
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
        pass
    # Try with a MagicMock for each required arg
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
        args.append(MagicMock())
    try:
        return cls(*args)
    except Exception:
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


class _ProducerOps:
    def __init__(self, modules: list[Any]) -> None:
        self._modules = modules
        self._classes = _all_classes(modules)
        self._instance_cache: dict[type, Any] = {}

    def ingest(self, body: bytes | str, headers: dict[str, str]) -> Any:
        fn = _find_callable(self._modules, self._classes, INGEST_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no ingest_event")
        # Try (body, headers) and (headers, body)
        for args in ((body, headers), (headers, body)):
            try:
                return fn(*args)
            except TypeError:
                continue
            except (ValueError, RuntimeError):
                raise
        raise LookupError("no working ingest arg ordering")

    def publish(self, event: Any) -> Any:
        fn = _find_callable(self._modules, self._classes, PUBLISH_NAMES, self._instance_cache)
        if fn is None:
            raise LookupError("no publish_event")
        return fn(event)

    def kafka_messages(self) -> list[dict[str, Any]]:
        return list(_kafka_mock_messages)

    def reset_kafka(self) -> None:
        _kafka_mock_messages.clear()


@pytest.fixture(scope="function")
def producer() -> _ProducerOps:
    return _ProducerOps(_import_modules())
