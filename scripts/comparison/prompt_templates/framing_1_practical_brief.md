Build a Kafka event-pipeline producer service in Python. The service
exposes a small REST handler that accepts JSON event payloads, validates
them, and publishes them to a Kafka topic for downstream consumption.

Each accepted event gets a generated UUID, a server-side timestamp, and
a header set carrying request metadata. Invalid inputs (empty payload,
malformed JSON, missing required headers) get rejected with a 400. The
published Kafka message preserves the original payload structure plus
the server-added fields.

The service should be testable end-to-end, including the Kafka publish
step (use a fake/in-memory Kafka client for tests). Keep domain logic
separate from Kafka-specific code so the publisher could be swapped for
SQS later.

OUTPUT FORMAT
  Emit each source file as a fenced code block immediately preceded by a
  header line of the form `### File: path/to/file.py`. The project
  should follow Clean Architecture layers under src/domain/,
  src/application/, src/infrastructure/, src/interface/. Emit one class
  per file. Also emit a tests/conftest.py that exposes a
  `discover_implementation()` function returning a dict mapping behavior
  names to concrete callables. Emit nothing outside the code blocks.
