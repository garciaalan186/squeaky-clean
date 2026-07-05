# Architecture — Squeaky Clean

The framework eats its own dog food: it follows Clean Architecture itself, with `squeaky_clean/domain/` importing nothing, `squeaky_clean/application/` importing only domain, `squeaky_clean/infrastructure/` implementing domain ports, and `squeaky_clean/interface/` as the entry point.

## Three model tiers

Each tier maps to a different model size + temperature + prompt-cache policy.

| Tier | Default model | Temperature | Seeded? | What it does |
|---|---|---:|---|---|
| **Architect** | claude-sonnet-4-6 | 0 | seed=0 | Reads ProblemSpec, emits `ArchitectureSpec` in Squib. One call per run. |
| **Manager** | claude-sonnet-4-6 | 0 | seed=0 | TestArchitect, SecurityArchitect, InfrastructureChoiceArchitect, EngineeringManager. Mid-tier orchestration. |
| **ICP** | claude-haiku-4-5 | 0.2 | seed=run.seed | Implements one class. Parallelized N-wide. Cost driver. |
| **Fixer** | claude-sonnet-4-6 | 0 | seed=0 | Single retry pass when a generated test fails. |

`--deterministic` pins every tier to `temperature=0, seed=0` for byte-identical replay. `temperature=0` alone doesn't guarantee determinism on the Anthropic API — we additionally use a content-addressed prompt cache to memoize identical requests.

## Agent hierarchy

```
                       ┌──────────────────────────┐
                       │   PrincipalArchitect     │  Architect tier
                       │   (1 call per run)       │
                       └────────────┬─────────────┘
                                    ▼
                       ┌──────────────────────────┐
                       │  ArchitectureSpec        │  multi-MODULE Squib
                       │  (validated DAG)         │
                       └────────────┬─────────────┘
                                    ▼
   ┌────────────────────────────────┼────────────────────────────────┐
   ▼                                ▼                                ▼
┌─────────────┐         ┌────────────────────┐         ┌──────────────────────────┐
│ TestArch.   │         │ SecurityArchitect  │         │ InfraChoiceArchitect     │  Manager tier
│ (per mod)   │         │ (per module)       │         │ (per category, MCDA)     │  (parallel)
└──────┬──────┘         └─────────┬──────────┘         └──────────────┬───────────┘
       │                          │                                   │
       │                          ▼                                   │
       │                   SecurityConcerns ───────────────┐          │
       │                                                    │          │
       │                                                    ▼          │
       │                                         ┌────────────────────┐│
       │                                         │ Tier C ICPs        ││
       │                                         │ (15 categories)    ││
       │                                         └─────────┬──────────┘│
       ▼                                                   │           │
┌──────────────────────────────────────────────────────────────────────┐
│                  OrchestrateArchitecture                             │
│       (parallel ICP fan-out across all classes; ≤ max_parallel)      │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
                     ┌──────────────────────┐
                     │  ImplementClass × N  │   ICP tier
                     └──────────┬───────────┘
                                ▼
                     ┌──────────────────────────────────────┐
                     │  IntegrateModule                     │
                     │  • writes layered src/<layer>/<mod>/ │
                     │  • runs DependencyRule validator     │
                     │  • writes manifests (pom/Cargo.toml/ │
                     │    requirements.txt/go.mod/...)      │
                     │  • emits main.py composition root    │
                     │  • shells to test runner             │
                     └──────────────────────────────────────┘
```

## Squib — the instruction set

The compact text format passed from PrincipalArchitect to ICPs.

```
MODULE Tasks
LAYER Domain
EXPORTS [Todo, Title]
DEPENDS []
CLASSES {
  Title -> ValueObject {
    fields:     [value: str]
    methods:    []
    invariants: ["value must not be empty"]
  }
  Todo -> Entity {
    fields:     [id: str, title: Title, is_complete: bool = false]
    methods:    [mark_complete(): None]
    depends:    [Title]
    invariants: []
  }
}
INVARIANTS []

MODULE TaskRepository
LAYER Application
EXPORTS [TaskRepositoryPort]
DEPENDS [Tasks::Todo]
CLASSES {
  TaskRepositoryPort -> Gateway {
    fields:  []
    methods: [save(todo: Todo): None, find_by_id(id: str): Todo, find_all(): Todo[]]
    depends: [Todo]
  }
}
```

Full grammar in [`squib.md`](squib.md).

## Tier C — generalized infrastructure

The *generalized infrastructure layer* (Milestone H) adds **technology-specific code generation** for 15 infrastructure categories (blob_storage, kv_cache, message_queue, rest_server_handler, etc.). The architect picks a category; the framework's `TechSpecResolver` picks a technology (boto3 vs azure-blob, Kafka vs RabbitMQ); the Tier C ICP emits the SDK-coupled adapter.

A separate document at [`infrastructure_layer_design.md`](infrastructure_layer_design.md) covers the full three-tier design (Tier C / Tier T / Tier B), the MCDA scoring algorithm, and the `--infra={manual,auto}` rollout strategy.

## Multi-language

Six languages share the same architecture orchestration; per-language adapters cover:

- ICP specs (per-pattern, per-language) — `squeaky_clean/interface/agent_specs/icps/<lang>/...`
- TestArchitect specs (per-language test-framework idioms)
- Granularity rules (per-language source-size enforcement)
- Test runner adapters (pytest / mvn / cargo / go test / npm test)
- Build-manifest generators (pyproject.toml / pom.xml / Cargo.toml / go.mod / package.json)
- Composition-root generators (Flask app.run / SpringApplication.run / axum::serve / etc.)
- Implementation-class parsers (per-language class-declaration syntax recognition)

A registry-driven `LanguageAdapterSelector` (registry coverage validated by unit test) dispatches per `target_language`.

## Architecture Recovery — the inverse pipeline

The same orchestration runs backward. **Agentic Architecture Recovery** ingests a brownfield project and rebuilds it as Clean Architecture, reusing the forward pipeline for regeneration.

```
brownfield project
   │  (per-language ClassCatalogExtractor: Python AST, Java/JS/TS regex)
   ▼
ClassCatalog ──► LayerAssigner ──► PatternClassifier ──► ModuleDecomposer
   │                                                          │
   │                                                          ▼
   │                                              ArchitectureSpec (faithful Squib)
   │                                                          │
   ├──► ViolationAnalysis (framework-coupling, dependency-rule, cyclic, ...)
   │            │
   │            ▼   InteractiveTriage (opt-out) ──► RefactorPlan
   │                         │
   │                         ▼
   │                RefactorPhase (1→N Entity+Repository+Adapter split)
   │                         │
   ▼                         ▼
recovered.squib      refactored.squib ──► SuppliedArchitectureDesigner ──► forward pipeline
```

The key property: **everything after ingest is language-neutral.** Layer assignment, pattern classification, decomposition, violation analysis, and refactoring all operate on the language-agnostic `ClassCatalog` / `ArchitectureSpec`, so a new source language needs only a new `ClassCatalogExtractor` behind the port + factory. The `SuppliedArchitectureDesigner` short-circuits the PrincipalArchitect so a signed-off Squib *is* the architecture that gets regenerated. Full design: [`architecture_recovery.md`](architecture_recovery.md).

## Cross-cutting concerns

- **Prompt cache.** `--prompt-cache` (default on) + `cache_control: {"type": "ephemeral"}` on stable prefixes. Per-tier hit ratio + savings reported in SUMMARY.md.
- **Cost budget.** `--max-cost-usd <N>` triggers graceful exit with `BUDGET_EXIT.txt` + partial-results report.
- **Resumable runs.** `--resume <run_dir>` re-attaches a crashed run via per-stage CHECKPOINT.json.
- **Replicates.** `--replicates N` runs N seeds + reports mean ± stddev across runs.
- **Per-agent eval.** `eval/per_agent/fixtures/` + scoring functions per agent class for unit-eval (decoupled from full pipeline).
- **Dashboard.** `--rebuild-dashboard` aggregates `meta-evaluation-results/` history into a static HTML chart.

## See also

- [`overview.md`](overview.md) — 5-min pitch
- [`squib.md`](squib.md) — Squib grammar reference
- [`writing_a_problem_spec.md`](writing_a_problem_spec.md) — author's guide
- [`extending.md`](extending.md) — custom-pattern hook + custom Tier C agents
- [`architecture_recovery.md`](architecture_recovery.md) — the inverse (brownfield → Clean Architecture) pipeline
- [`infrastructure_layer_design.md`](infrastructure_layer_design.md) — full Tier C design
