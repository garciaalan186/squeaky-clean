# Overview — Squeaky Clean

A 5-minute read.

## The problem

LLM codegen has a Clean Architecture problem. "Write me a Spring Boot service that publishes to Kafka" produces a single 200-line file with the controller talking directly to `KafkaTemplate`, the entity mutating to JSON inline, and zero separation between domain logic and infrastructure. It compiles. It runs. It's unmaintainable the moment you swap Kafka for SQS.

What's missing is **architectural discipline**: the discipline that says domain entities don't import frameworks; that ports live in the application layer and adapters live in the infrastructure layer; that crossing a bounded-context boundary requires an explicit contract. That discipline is what separates a one-shot demo from production-grade code.

## The approach

Squeaky Clean splits the codegen problem into three layers, each with its own constraints:

1. **PrincipalArchitect (Architect tier)** — reads a `ProblemSpec`, emits a structured `ArchitectureSpec` in Squib. Decides bounded contexts, classes per context, layer assignment, dep edges. Deterministic by default.
2. **ImplementClass (ICP tier)** — for each class in the architecture, runs a parallelizable Implements-Clean-Pattern agent. Each ICP specializes in exactly one GoF/DDD pattern (or a Tier C infrastructure category). One file in, one file out.
3. **IntegrateModule + ValidateArchitecture** — assembles the per-class outputs into a runnable project, validates dependency rules, runs the generated test suite, computes metrics.

The Squib between tiers is the **instruction set architecture**. It's compact (~200 chars per class), unambiguous (validated against a frozen grammar), and the architect's mistakes get caught at the spec layer rather than after generation.

## What you write

A `ProblemSpec` JSON:

```json
{
  "id": "TODO_API",
  "description": "Minimal Todo REST API with Flask + local-disk persistence.",
  "acceptance_criteria": [
    "Given a title 'buy milk', When create_todo is called, Then result is a Todo",
    "Given an empty title, When create_todo is called, Then an error is raised"
  ],
  "required_patterns": ["Entity", "ValueObject", "UseCase", "Repository", "Adapter"],
  "target_language": "python",
  "infrastructure_choices": [
    {"category": "rest_server_handler", "technology": "flask", "version_pin": "Flask==3.0"}
  ]
}
```

That's the entire input. The framework derives module decomposition, class assignments, port/adapter splits, dependency-rule enforcement, and a runnable composition root.

## What you get

```
output_dir/
├── src/
│   ├── domain/tasks/{todo.py, title.py, ...}
│   ├── application/tasks/{create_todo_use_case.py, task_repository_port.py, ...}
│   ├── infrastructure/task_repository/{local_disk_task_repository.py, ...}
│   └── interface/task_handlers/{flask_task_handler.py, ...}
├── tests/
│   └── ... (one test file per generated class, mirrored layout)
├── main.py                    # composition root: instantiates everything, runs Flask
├── requirements.txt           # generated from resolved TechSpecs
└── eval_report.json           # tests_pass, cost, tokens, ACS, etc.
```

`pip install -r requirements.txt` then `pytest tests/` against the generated project. It runs.

## Cost and complexity

| Problem class | Modules | Classes | Cost | Wall ms |
|---|---:|---:|---:|---:|
| P0 Calculator | 1 | ~5 | $0.05 | ~6,000 |
| P1 Todo API | 3 | ~12 | $0.10 | ~10,000 |
| P3 Chat App | 8 | ~60 | $1.50 | ~60,000 |
| Twitter Clone | 9 | ~22 | $0.40 | ~30,000 |
| Distributed event pipeline (per service) | 4 | ~10 | $0.30 | ~15,000 |

See [`BENCHMARK_METHODOLOGY.md`](../BENCHMARK_METHODOLOGY.md) for the Architectural Complexity Score (ACS) that normalizes these across problem complexity — `$/ACS-unit` is a fairer cross-problem efficiency measure than raw `$/run`.

## Differentiators

- **Deterministic runs.** Same `ProblemSpec` + `--deterministic` produces byte-identical architecture.squib across two runs. Proven; reproduced in CI.
- **Cross-language parity.** The same `ProblemSpec` switching `target_language` to `java` produces the equivalent Spring Boot project. Same architectural shape; idiomatic SDK calls.
- **Cross-service contract fidelity.** When two services produce/consume the same Kafka topic, Squeaky Clean's Contract Registry enforces field-shape agreement across language boundaries — the consumer's `ConsumedEvent` carries the producer's contract field names verbatim, with case-tolerance for languages whose conventions would otherwise rename `received_at` → `receivedAt`.
- **Architectural discipline preserved.** Domain layer never imports infrastructure. Concrete adapters never live in the application layer. Generated code passes the framework's own dependency rule.

## What it's not

- **Not a one-shot LLM call.** Squeaky Clean orchestrates dozens of LLM calls per run, parallelized, with prompt caching and a strict per-tier cost budget.
- **Not a substitute for understanding your domain.** The framework asks you to declare your bounded contexts in `required_bounded_contexts` and your acceptance criteria in `acceptance_criteria`. Garbage spec → garbage generation.
- **Not a code-completion tool.** Squeaky Clean produces complete projects from spec, not autocomplete suggestions in your editor.

## The other direction: recovery

The same discipline runs in reverse. **Agentic Architecture Recovery** points the framework at an existing brownfield project (Python, JavaScript, TypeScript, or Java), ingests it into a faithful `Squib`, analyzes it for Clean-Architecture violations, and — with your sign-off — refactors framework-coupled classes into Entity + Repository + Adapter before regenerating. Messy legacy code in, a freshly generated Clean-Architecture project out. See [Agentic Architecture Recovery](architecture_recovery.md).

## Next steps

- [Quickstart](../README.md#quickstart) — generate the Todo API in 15 seconds.
- [Architecture deep-dive](architecture.md) — three model tiers + agent hierarchy + the Squib grammar.
- [Writing a ProblemSpec](writing_a_problem_spec.md) — walkthrough + best practices.
- [Agentic Architecture Recovery](architecture_recovery.md) — the inverse path: brownfield → recovered Squib → refactor → regenerate.
