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

That command produces a runnable Flask Todo API from a sample spec.

## What's different

The market has plenty of "AI writes your app" demos. Squeaky Clean's differentiators:

- **Cached replay.** All tiers pin `temperature=0` for architectural decisions; every LLM call routes through a content-addressed response cache. Repeats of the same input return cached output. First-call output depends on the API's runtime behavior.
- **Six languages.** Same `ProblemSpec`, change `target_language: "python" | "java" | "go" | "rust" | "javascript" | "typescript"`. 60 Tier-C atomic agents across 15 infrastructure categories.
- **Real SDK integration.** Generated adapters import `boto3.S3Client` / `KafkaTemplate` / `redis.Client` / etc. and call SDK methods directly.
- **Cross-service contract fidelity.** When two services produce/consume the same Kafka topic, Squeaky Clean's Contract Registry enforces field-shape agreement across language boundaries with case-tolerant validation.
- **Port/adapter discipline.** Domain layer never imports infrastructure. Concrete adapters never live in the application layer. The generated `dependency_rule.py` validator catches violations.
- **Benchmarks page** with measured `tests_pass`, cost, and wall-clock figures traceable to specific run IDs. See `BENCHMARK_METHODOLOGY.md` for the methodology and the docs site for the latest results.

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

`✅` = full Tier C atomic agent + ≥2 TechSpec snapshots + e2e build available. `⏳` = on the roadmap.

## Known limits

- **`tests_pass`.** Per-language `tests_pass` figures depend on the toolchain availability of the run environment (per-language test runners report zero when their toolchain is missing rather than crashing the pipeline). Current measured figures by run ID are on the Benchmarks page in the docs.
- **Cost.** Cost figures by problem and by run ID are on the Benchmarks page. Methodology, including the Architectural Complexity Score (ACS) for cross-problem normalization, is in `BENCHMARK_METHODOLOGY.md`.
- **TestArchitect verb hallucination.** When the architect's emitted Squib doesn't declare a verb the acceptance criteria reference, the generated test calls `pytest.fail("verb X not in ModuleSpec")` rather than inventing methods. K5's per-module criterion filtering bounds this; remaining residue is genuine impl/test mismatches.

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

Three model tiers: Architect (high-parameter), Manager (mid), atomic agent (compact, lightly sampled, parallelized). Cost is dominated by the atomic-agent tier.

## Examples

- [`examples/todo_api/`](examples/todo_api/) — smallest end-to-end (Flask Todo REST API)
- [`examples/twitter_clone/`](examples/twitter_clone/) — multi-context with rich domain semantics
- [`examples/event_pipeline/`](examples/event_pipeline/) — distributed two-service Kafka pipeline (cross-service contract fidelity)

## Documentation

Docs live at https://docs.squeakyclean.ai. Highlights:

- **Why Squeaky Clean?** — design philosophy + 5-minute pitch.
- **Architecture deep-dive** — three tiers + agent hierarchy.
- **Squib grammar** — the inter-tier instruction set.
- **Author your first ProblemSpec** — walkthrough + best practices.
- **Custom patterns** — extension hook + custom Tier C agents.
- **Infrastructure layer design** — full design doc.
- **Benchmarks** — methodology + measured run data.
- **Roadmap** — public, milestone-level.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). The framework eats its own dog food: every Hard Rule it enforces on generated code applies to its own source. PRs welcome on RFCs (12 open design questions in `docs/infrastructure_layer_design.md` §10).

## License

[Apache 2.0](LICENSE). You own what you generate. Anthropic's IP terms apply to LLM output.

## Project status

**Active development.** 60 Tier C atomic agents across 15 infrastructure categories; six target languages. Pre-launch milestone (Milestone K) complete. Looking for early users with real ProblemSpecs.
