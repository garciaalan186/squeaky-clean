# Example — Event Pipeline (cross-language, distributed)

Two services that demonstrate Squeaky Clean's distributed-architecture capabilities:

- **Producer**: REST endpoint receives event payloads via `POST /events` and forwards them (with HTTP headers) to Kafka topic `events.raw`.
- **Persister**: Kafka consumer reads from `events.raw` and archives each event to blob storage at key `events/<received_at>-<id>.json`.

The two services agree on a cross-service **contract** (the JSON envelope on `events.raw`), which Squeaky Clean enforces via its Contract Registry — the consumer's `ConsumedEvent` entity must declare exactly the same field names as the producer's `IngestedEvent`, with case-tolerant matching across languages.

## Run

```bash
export ANTHROPIC_API_KEY="<your-key>"  # secret-scan: allow

# Producer first — registers the events.raw contract
python -m src.interface.cli --problem-file examples/event_pipeline/producer_problem.json --infra=auto

# Persister second — resolves the contract from the registry
python -m src.interface.cli --problem-file examples/event_pipeline/persister_problem.json --infra=auto
```

The same shape works in 6 supported languages by changing `target_language` and the `infrastructure_choices` to the language-appropriate technologies (e.g. Spring Boot + spring-kafka for Java, axum + rdkafka for Rust).

## What this demonstrates

- **Contract fidelity** — the persister's `ConsumedEvent` carries the producer's contract field names verbatim (id / received_at / headers / payload), with case-tolerance for languages whose conventions would otherwise rename `received_at` → `receivedAt`.
- **Tier C infrastructure** — adapters wire to `confluent-kafka` and `pathlib` (or language equivalents) with real SDK calls, not stubs.
- **Composition root generation** — each service emits its own `main.py` / `App.java` / `main.go` / `main.rs` ready to run.
- **Cost** — ~$0.30 per service. Two services: ~$0.60 total.

## See also

- `examples/event_pipeline/producer_problem.json` — Python producer ProblemSpec
- `examples/event_pipeline/persister_problem.json` — Python persister ProblemSpec
- `docs/architecture.md` — the three-tier model that makes this work
- `BENCHMARK_METHODOLOGY.md` — Architectural Complexity Score (event-pipeline producer ≈ 11 ACS units)
