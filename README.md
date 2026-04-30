# Squeaky Clean

```
   _____________   ° o °
  /             \    o
 |  SQUEAKY     |   ° o
 |   CLEAN      |   o °
  \_____________/   ° o
```

**Generate Clean-Architecture-shaped applications from one ProblemSpec — across Python, Java, Go, Rust, JavaScript, and TypeScript, with real infrastructure adapters.**

[![CI](https://github.com/garciaalan186/squeaky-clean/actions/workflows/ci.yml/badge.svg)](https://github.com/garciaalan186/squeaky-clean/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-1508_passing-brightgreen.svg)](#)
[![mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](#)

---

## What it does

You write one declarative `ProblemSpec` JSON. Squeaky Clean produces a buildable, testable application that follows Clean Architecture (Robert C. Martin) and SOLID principles, using GoF + DDD patterns as the shared vocabulary between agent tiers.

```bash
# Once published to PyPI:
pip install squeaky-clean

# Until then (or for the latest main):
pip install git+https://github.com/garciaalan186/squeaky-clean.git

export ANTHROPIC_API_KEY="<your-key>"  # secret-scan: allow
squeaky generate --problem-file examples/todo_api/todo_problem.json --infra=auto
```

That command produces a runnable Flask Todo API in ~15 seconds for ~$0.07.

## What's different

The market has plenty of "AI writes your app" demos. Squeaky Clean's differentiators:

- **Deterministic by default.** `temperature=0` for architectural decisions; same ProblemSpec produces byte-identical architecture.notation across runs.
- **Six languages at parity.** Same `ProblemSpec`, change `target_language: "python" | "java" | "go" | "rust" | "javascript" | "typescript"`. 60 Tier-C ICPs across 15 infrastructure categories.
- **Real SDK integration.** Generated adapters import `boto3.S3Client` / `KafkaTemplate` / `redis.Client` / etc. and call real methods — not stubs.
- **Cross-service contract fidelity.** When two services produce/consume the same Kafka topic, Squeaky Clean's Contract Registry enforces field-shape agreement across language boundaries with case-tolerant validation.
- **Port/adapter discipline preserved.** Domain layer never imports infrastructure. Concrete adapters never live in the application layer. The generated `dependency_rule.py` validator catches violations.
- **Honest tests_pass numbers published.** See the [coverage matrix](#coverage-matrix) below — we publish what works AND what doesn't.

## Quickstart

```bash
# Install — once published to PyPI:
pip install squeaky-clean

# Or install directly from GitHub (works today):
pip install git+https://github.com/garciaalan186/squeaky-clean.git

# Or clone and install in editable mode for development:
git clone https://github.com/garciaalan186/squeaky-clean.git
cd squeaky-clean
pip install -e ".[dev]"

# Set your Anthropic API key
export ANTHROPIC_API_KEY="<your-key>"  # secret-scan: allow

# Generate a Todo API (smallest example)
squeaky generate --problem-file examples/todo_api/todo_problem.json --infra=auto

# The output dir contains: src/, tests/, requirements.txt, main.py
# Install deps and run tests
cd <output_dir>
pip install -r requirements.txt --target .test-deps/
PYTHONPATH=.:.test-deps python -m pytest tests/ -q
```

## Coverage matrix

| Category | Python | Java | Go | Rust | JS | TS |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| ddd_clean (Entity, ValueObject, SimpleClass, Strategy) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| security ICPs (5 categories) | ✅ | ✅ | ✅ | ✅ | ⏳ | ⏳ |
| blob_storage | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| kv_cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| relational_db / document_db | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| message_queue (producer + consumer) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| stream_processor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| rest_client / rest_server_handler | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| grpc_client / grpc_server_handler | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| websocket_server_handler | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| observability_logger | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| secrets_provider | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

`✅` = full Tier C ICP + ≥2 TechSpec snapshots + verified e2e build. `⏳` = on the roadmap.

## Honest limits

What we publish that other tools don't:

- **`tests_pass` is a real number, not a marketing claim.** On the canonical event-pipeline benchmark: Python 0.40, Java/Go/Rust/JS/TS 0.00 (toolchains report zero on availability fallback rather than crashing the pipeline; `mvn -q compile` does succeed against the generated Java).
- **Cost is published.** $0.05–$0.10 for P0 (todo_api), $0.30–$0.40 for distributed multi-service problems. See `BENCHMARK_METHODOLOGY.md` for the Architectural Complexity Score (ACS) that normalizes cost across heterogeneous problem complexity.
- **Honest failure modes documented.** TestArchitect can hallucinate verbs not in the ModuleSpec — we emit `pytest.fail("verb X not in ModuleSpec")` honestly rather than inventing methods. K5's per-module criterion filtering bounds this; remaining residue is genuine impl/test mismatches.

## How it works (60 seconds)

```
ProblemSpec (JSON)
       │
       ▼
PrincipalArchitect ──► §Notation ModuleSpec (text)
       │                   │
       │                   ▼
       │            ArchitectureSpec (multi-MODULE, validated DAG)
       │                   │
       │                   ▼
       │             OrchestrateArchitecture
       │                   │
       │            (parallel fan-out per module)
       │                   ▼
       │             ImplementClass × N (Tier C / ICP)
       │                   │
       │                   ▼
       └────► IntegrateModule → src/ + tests/ + main.py + requirements.txt
                                                    │
                                                    ▼
                                          mvn / cargo / pytest / etc.
```

Three model tiers — Architect (high-parameter, deterministic), Manager (mid, deterministic), ICP (low, lightly sampled, parallelized). Cost is dominated by ICPs.

## Examples

- [`examples/todo_api/`](examples/todo_api/) — smallest end-to-end (Flask Todo REST API)
- [`examples/twitter_clone/`](examples/twitter_clone/) — multi-context with rich domain semantics
- [`examples/event_pipeline/`](examples/event_pipeline/) — distributed two-service Kafka pipeline (cross-service contract fidelity)

## Documentation

- [`docs/overview.md`](docs/overview.md) — 5-minute pitch
- [`docs/architecture.md`](docs/architecture.md) — three tiers + agent hierarchy
- [`docs/notation.md`](docs/notation.md) — §Notation grammar reference
- [`docs/writing_a_problem_spec.md`](docs/writing_a_problem_spec.md) — walkthrough + best practices
- [`docs/extending.md`](docs/extending.md) — custom-pattern hook + custom Tier C agents
- [`docs/infrastructure_layer_design.md`](docs/infrastructure_layer_design.md) — full design doc for the generalized infrastructure layer
- [`docs/roadmap.md`](docs/roadmap.md) — public, milestone-level

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). The framework eats its own dog food: every Hard Rule it enforces on generated code applies to its own source. PRs welcome on RFCs (12 open design questions in `docs/infrastructure_layer_design.md` §10).

## License

[Apache 2.0](LICENSE). You own what you generate. Anthropic's IP terms apply to LLM output.

## Project status

**Active development.** 1500+ tests; mypy strict clean; 60 Tier C ICPs; 6 languages. Pre-launch milestone (Milestone K) complete. Looking for early users with real ProblemSpecs.
