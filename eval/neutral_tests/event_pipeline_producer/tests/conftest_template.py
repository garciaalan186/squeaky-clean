"""Template / contract for the project's real ``tests/conftest.py``.

The project under test must provide its own ``tests/conftest.py`` that:

  1. Defines ``discover_implementation()`` returning a dict with the keys
     documented below.
  2. Exposes an ``implementation`` pytest fixture that returns the result
     of ``discover_implementation()``.

The acceptance suite (``tests/test_acceptance.py``) only depends on this
contract; it knows nothing about the project's internal modules.

Required keys in the dict returned by ``discover_implementation()``:

    "ingest_event"
        Callable(body: bytes, headers: dict) -> IngestedEvent.
        Validates the body (non-empty, <= 1 MB) and constructs an event.

    "IngestedEvent"
        The class used for ingested events. Must expose at least the
        attributes (or mapping keys) ``id``, ``received_at``,
        ``headers``, ``payload``.

    "publish_event"
        Callable(event: IngestedEvent, producer=...) -> None.
        Serializes the event to JSON and publishes it to the
        ``events.raw`` topic via ``producer``. Raises on Kafka failure.

    "make_ingested_event"
        Factory: (body: bytes, headers: dict) -> IngestedEvent.
        Convenience constructor used by tests that need a valid event
        without going through ``ingest_event``.

    "make_fake_producer"
        Factory: () -> producer-like object with a ``.messages`` list
        attribute. Each publish appends either a ``(topic, payload)``
        tuple or a dict containing ``topic`` and ``value`` keys.

    "make_unreachable_producer"
        Factory: () -> producer-like object whose publish operation
        raises an exception (simulating Kafka being unreachable).
"""

import pytest


def discover_implementation():
    """Return a dict mapping behavior keys to concrete callables/classes.

    The real project must override this. The template raises so a missing
    project-side conftest is obvious.
    """
    raise NotImplementedError(
        "The project under test must provide tests/conftest.py with a real "
        "discover_implementation()."
    )


@pytest.fixture
def implementation():
    return discover_implementation()
