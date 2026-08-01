# Architecture — Squeaky Clean

Squeaky Clean eats its own dog food: it follows Clean Architecture itself, with `squeaky_clean/domain/` importing nothing, `squeaky_clean/application/` importing only domain, `squeaky_clean/infrastructure/` implementing domain ports, and `squeaky_clean/interface/` as the entry point.

Inside the application layer, packaging is by component rather than by type. `squeaky_clean/application/generation/` is the product pipeline (`architecture/`, `emission/`, `integration/`, `notation/`, `recovery/`, `repair/`, `security/`, `techspec/`, `testgen/`, `validation/`); `squeaky_clean/application/evaluation/` is the eval harness (`eval/` with `metrics/`, `report/`, `resume/`, `run/`, `sweep/`); `squeaky_clean/application/shared/` is what both build on (`config/`, `gateways/`, `io/`, `language/`, `mcda/`, `problem/`). Data-carrying types live beside the code that uses them. The permitted edges are `generation → shared` and `evaluation → {generation, shared}` — `generation` never imports `evaluation`, so the product carries no dependency on its own harness. `ComponentDependencyRule` and `PackageCohesionRule` (`squeaky_clean/domain/rules/`) enforce that DAG and the Common Closure bound — no package over 20 direct modules, no type-named catch-all packages — in the framework's self-conformance gate (`tests/self_conformance/`), which runs in CI alongside ruff, `mypy --strict`, and the drift guards. The same gate bans f-string-driven reflection framework-wide: `setattr` / `getattr` called with a dynamically built attribute name is a violation, reported under the `ReflectionBan` key prefix. Two further framework-only rules police the injection regime — `FsPortBypass`, a raw `Path.write_text` / `write_bytes` anywhere under `application/generation/**` or `application/evaluation/**`, and `ImpureConstruction`, an I/O-touching class constructed anywhere under `application/**` instead of injected.

## Three model tiers

Each tier maps to a different model size + temperature + prompt-cache policy.

| Tier | Default model | Temperature | Seeded? | What it does |
|---|---|---:|---|---|
| **Architect** | claude-sonnet-5 | 0 | seed=0 | RequirementCompiler: reads ProblemSpec, emits `ArchitectureSpec` in Squib. One call per run. |
| **Manager** | claude-sonnet-5 | 0 | seed=0 | OracleCompiler, ThreatAnalyzer, layer verifiers, InfrastructureChoiceArchitect, ModuleLowerer. Mid-tier orchestration. |
| **ICP** | claude-haiku-4-5 | 0.2 | seed=run.seed | Implements one class. Parallelized N-wide. Cost driver. |
| **Fixer** | claude-sonnet-5 | 0 | seed=0 | Single retry pass when a generated test fails. |

Concrete model identifiers live in exactly one place — `squeaky_clean/infrastructure/llm/model_catalog.py::ModelId` — which both `ModelRouter` and the pricing table read from, so no other layer names a bare model string and bumping a tier's model is a one-line change. The full-quality mapping (`ModelRouter.DEFAULT_MAPPING`) puts the Architect tier on `claude-opus-4-8`; the CLI's `RouterFactory` applies the cost override that demotes it to `claude-sonnet-5`, and that override is derived from `DEFAULT_MAPPING` rather than a second table, so it can't diverge on a model bump. The column above is what a default CLI run resolves to. Whatever a given run actually resolved — including `--model-override` — is rendered from the router into that run's SUMMARY.md and manifest.

`--deterministic` pins every tier to `temperature=0, seed=0` for byte-identical replay. `temperature=0` alone doesn't guarantee determinism on the Anthropic API — we additionally use a content-addressed prompt cache to memoize identical requests.

## Agent hierarchy

```
                       ┌──────────────────────────┐
                       │   RequirementCompiler    │  Architect tier
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
│ OracleComp. │         │ ThreatAnalyzer     │         │ InfraChoiceArchitect     │  Manager tier
│ (per mod)   │         │ (per module)       │         │ (per category, MCDA)     │  (parallel)
└──────┬──────┘         └─────────┬──────────┘         └──────────────┬───────────┘
       │                          │                                   │
       │                          ▼                                   │
       │                   SecurityConcerns ───────────────┐          │
       │                                                    │          │
       │                                                    ▼          │
       │                                         ┌────────────────────┐│
       │                                         │ Tier C Emitters    ││
       │                                         │ (15 categories)    ││
       │                                         └─────────┬──────────┘│
       ▼                                                   │           │
┌──────────────────────────────────────────────────────────────────────┐
│                  OrchestrateArchitecture                             │
│    (parallel emitter fan-out across all classes; ≤ max_parallel)     │
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
                     │  • writes manifests (pom.xml/        │
                     │    requirements.txt/package.json/...)│
                     │  • emits main.py composition root    │
                     │  • shells to test runner             │
                     └──────────────────────────────────────┘
```

## Squib — the instruction set

The compact text format passed from RequirementCompiler to emitters.

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

## ProblemSpec — behavior vs structure

A `ProblemSpec` splits cleanly along what a Squib can and cannot carry, and exposes each half as a read-only view. The flat fields stay the construction surface, so authoring a spec is unchanged.

| View | Type | Carries | Where it comes from |
|---|---|---|---|
| `.behavior` | `BehaviorSpec` | `acceptance_criteria`, `produces_contracts`, `consumes_contracts`, `data_classification`, `expected_outcomes` | Always authored — the irreducible acceptance oracle, the part no Squib encodes. The OracleCompiler compiles tests from it. |
| `.structural_hints` | `StructuralHints` | `required_patterns`, `required_bounded_contexts`, `expected_module_count`, `expected_class_count` | Authored on the greenfield path (hints to the RequirementCompiler); derivable from the IR on the squib-first and recovery paths. |

`derive_structural_hints_from_squib(architecture)` (`squeaky_clean/application/evaluation/eval/metrics/derive_structural_hints.py`) is the deterministic projection of an `ArchitectureSpec` onto `StructuralHints` — no LLM call. It generalizes the recovery path's `ProblemSpecSynthesizer`: when the structure already exists, only the behavioral half has to be supplied.

## Tier C — generalized infrastructure

The *generalized infrastructure layer* (Milestone H) adds **technology-specific code generation** for 15 infrastructure categories (blob_storage, kv_cache, message_queue, rest_server_handler, etc.). The architect picks a category; the framework's `TechSpecResolver` picks a technology (boto3 vs azure-blob, Kafka vs RabbitMQ); the Tier C emitter emits the SDK-coupled adapter.

A separate document at [`infrastructure_layer_design.md`](infrastructure_layer_design.md) covers the full three-tier design (Tier C / Tier T / Tier B), the MCDA scoring algorithm, and the `--infra={manual,auto}` rollout strategy.

## Multi-language

Four languages — Python, JavaScript, TypeScript and Java — share the same architecture orchestration; per-language adapters cover:

- Emitter specs (per-pattern) — the 11 DDD/Clean patterns ship as one complete spec per language under `squeaky_clean/interface/agent_specs/emitters/<lang>/...`, and the 23 creational, structural and behavioral patterns are authored once as cross-language templates under `emitters/_shared/` and composed with the language's profile; between them all 34 patterns are covered in each of the four languages, see [Emitter spec composition](#emitter-spec-composition)
- OracleCompiler specs (per-language test-framework idioms)
- Granularity rules (per-language source-size enforcement)
- Test runner adapters (pytest / mvn / npm test)
- Build-manifest generators (pyproject.toml / pom.xml / package.json)
- Composition-root generators (Flask app.run / SpringApplication.run / Express listen / etc.)
- Implementation-class parsers (per-language class-declaration syntax recognition)

`LanguageAdapterRegistry` (`squeaky_clean/interface/cli/language_adapter_registry.py`) is the one per-language dispatch table, its coverage validated by unit test. A single entry per language holds every runtime adapter: the test-runner factory (it takes an exclude glob plus the composition root's `RunLogger`) together with that language's functional-test exclude pattern, the granularity rule, the integration bootstrap, the implementation-class parser, the dependency installer (it takes the same logger), and the optional ahead-of-time compiler — TypeScript and Java have one; Python, JavaScript, Go and Rust do not. The adapter selector, the compiler factory and the test-runner factory are thin views over that table, so adding a target language means adding one entry to it; `LanguageAdapterSelector` and `LanguageTestRunnerFactory` take the logger and pass it down, so a failing toolchain subprocess lands in the structured JSON run log instead of being swallowed. Left unwired they fall back to a silent null logger. Go and Rust stay registered even though their emitter-spec fleets are archived, so recovered and replayed runs in those languages still dispatch.

## Emitter spec composition

A pattern emitter is authored in one of two shapes. The first is a complete spec per language at `emitters/<language>/<category>/<Pattern>Emitter.md` — four near-identical files kept in step by hand. The second is a single cross-language template at `emitters/_shared/<category>/<Pattern>Emitter.md`, composed at emission time with a per-language profile at `emitters/_shared/profiles/<language>.md`; profiles ship for `python`, `javascript`, `typescript` and `java`.

Resolution is fallback-based (`ComposeEmitterSpec`, `squeaky_clean/application/generation/emission/composition/`): the shared template is used when one exists for the pattern, and otherwise the per-language file is loaded unchanged — so a pattern not yet cut over behaves exactly as before. A shared template with no matching language profile is an authoring error and raises loudly rather than silently degrading.

The template grammar is deliberately flat — blocks do not nest:

| Construct | Meaning |
|---|---|
| `{{profile:<block_name>}}` | Pulls in a named delta block from the composing language's profile. An unknown reference is left literal, the same convention the shared-spec composer uses. |
| `{{#lang:java}}` … `{{/lang}}` | A line-based conditional block; the opener accepts a comma list (`{{#lang:python,typescript}}`). Inner lines survive only for the listed languages, and the marker lines themselves never survive. Lines outside any block always survive. |

The existing language-toolkit placeholders are substituted afterwards, so a composed spec carries no unresolved `{{…}}`.

A profile file is markdown in which every `## <block_name>` heading opens a named block whose body runs until the next heading. The shipped profiles carry `language_name`, `fence_tag`, `input_suffix`, `file_preamble`, `abstract_idiom`, `concrete_idiom`, `style_rule`, `arg_note`, `import_rule`, `language_rules`, `error_rule`, `shadowing_rule`, `fields_rule`, `sibling_fields_rule`, `collection_default_rule`, `floor_expr`, `extra_constraints` and `polymorphism_note`. A block may legitimately be empty.

The creational, structural and behavioral families are authored as shared templates: 23 patterns in all — the 5 creational (Abstract Factory, Builder, Factory Method, Prototype, Singleton), the 7 structural (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy) and the 11 behavioral (Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor) — are one template plus the four language profiles, and `emitters/<language>/creational/`, `emitters/<language>/structural/` and `emitters/<language>/behavioral/` hold no pattern specs. The remaining 11 patterns — the DDD/Clean family — ship one complete spec file per language, 44 files in all.

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

The key property: **everything after ingest is language-neutral.** Layer assignment, pattern classification, decomposition, violation analysis, and refactoring all operate on the language-agnostic `ClassCatalog` / `ArchitectureSpec`, so a new source language needs only a new `ClassCatalogExtractor` behind the port + factory. The `SuppliedArchitectureDesigner` short-circuits the RequirementCompiler so a signed-off Squib *is* the architecture that gets regenerated. Full design: [`architecture_recovery.md`](architecture_recovery.md).

## Cross-cutting concerns

- **Prompt cache.** `--prompt-cache` (default on) + `cache_control: {"type": "ephemeral"}` on stable prefixes. Per-tier hit ratio + savings reported in SUMMARY.md. The cache key is the sha256 of the model, the prompts and the replicate id; temperature and seed are deliberately excluded, since neither is sent to the API and including them would only fragment the cache. A failed call is never stored: a response that timed out, and one whose content is empty or whitespace-only, are both skipped on write, so a failed model call can't be replayed as an empty result on every later run of the same prompt — it is retried live instead.
- **Replay-only runs.** `--replay-only` modifies a normal run (`--problem P0 --replay-only`) so every LLM call is served from the response cache. The live gateway is replaced in the chain by `CacheMissRaiser`, an `LLMGateway` implementation that raises on every call, so a prompt absent from the cache can never fall through to the API: the run fails with `ReplayCacheMissError` (a `RuntimeError`) carrying the model, the cache-key prefix and the head of the prompt, which identifies the drifted prompt from the error alone. Everything outside the LLM seam runs for real — parsing, routing, emission, integration, the generated project's test suite, scoring. The run costs $0 and needs no API key. `SQUEAKY_CACHE_DIR` overrides the cache directory; the default is unchanged at `meta-evaluation-results/cache/` next to the framework checkout. CI uses both together to replay P0 against a committed bundle at `tests/ci_replay_cache/` as a $0 end-to-end gate. A replay miss inside a sweep aborts the whole sweep rather than being scored as one problem's failure — it is an infrastructure signal, not a benchmark result.
- **Cost budget.** `--max-cost-usd <N>` is enforced pre-flight: each call reserves a conservative projected cost (input estimated from prompt length, output assumed to use the full `max_tokens`) against the cap before it runs, then settles the actual cost afterward — so a call that would blow the budget is never paid for, and parallel overshoot is bounded by the reservation rather than by racing threads each reading a below-cap total. Crossing the cap triggers graceful exit with `BUDGET_EXIT.txt` + partial-results report. A `--resume`d run seeds the gate with the spend recorded before the checkpoint.
- **Resumable runs.** `--resume <run_dir>` re-attaches a crashed run via per-stage CHECKPOINT.json.
- **Durable writes.** Framework-internal artifacts — run summaries, `CHECKPOINT.json`, the HTML dashboards, `architecture.notation`, `LATENCY_PERCENTILES.md` and the violation reports — are written through `atomic_write_text` (`squeaky_clean/application/shared/io/atomic_write.py`), which writes a sibling temp file and renames it into place. A reader therefore sees either the old contents or the new ones and never a partial, so a crash or a budget exit mid-write cannot leave behind a half-written file for a later `--resume` to parse as corrupt. Artifacts belonging to the generated project go through the `ProjectFileSystem` port instead.
- **No silent swallow.** A failure the pipeline survives is still recorded, and a failure it cannot survive says why. Under `--infra=auto`, every technology-spec source that fails emits a structured run-log event carrying its reason — `techspec_fs_miss`, `techspec_snapshot_rejected` (a bundled snapshot that is unreadable, is not a JSON object, fails schema validation or is rejected by the builder), `techspec_cache_rejected`, `techspec_source_failed` naming the source, and `techspec_stale_cache_used` when a grace-window entry is served through an outage — and when nothing resolves, `techspec_unresolvable` carries every reason, the stage logs `tech_spec_resolution_failed`, and the run fails with `TechSpecResolutionError` (a `TechSpecUnresolvableError` carrying the same `reasons` tuple) rather than degrading. Build-manifest generators raise `ManifestWriteError` on a failed write instead of returning `None`, so `None` from a generator means only "not applicable for this language"; `ManifestEmitter` catches it and logs a `<name>_emit_failed` event, keeping manifest emission best-effort but never silent. The remaining best-effort writes report the same way — `checkpoint_artifact_write_failed`, `sast_report_write_failed` and `notation_triage_write_failed` — and an unreadable run-metrics-history file, an unreadable model-pricing cache and an unparseable manager tech-spec repair reply emit a logged warning rather than being dropped. Full resolution contract in [`infrastructure_layer_design.md`](infrastructure_layer_design.md) §4.
- **Injection from the composition root.** Collaborators that touch the filesystem, the network or the environment are constructed once in `squeaky_clean/interface/cli/dependency_builder.py` and passed inward, never built inside an application class. `LoadAgentSpec` is a required constructor argument for `DesignArchitecture`, `GenerateTestArchitecture`, `GenerateSecurityTests`, `ReviewSecurity`, `VerifyLayer`, `ImplementClass`, `TechSpecComposer`, `ComposeAgentSpec` and `SecurityICPDispatcher`; `ProjectFileSystem` is required by `WiringGenerator`, `BuildManifestGenerator`, `SquibReviewGate`, `RecoveryEmitter`, `RefactorEmitter`, `RepairTestFile` and `ManifestEmitter`, and the standalone manifest generators (`go.mod`, `Cargo.toml`, `package.json`, `requirements.txt`, `tsconfig.json`) take a keyword-only `fs`. Every shell-out likewise sits behind a port implemented in infrastructure, so the application layer itself is subprocess-free. The self-conformance gate holds the line: `ImpureConstruction` flags an I/O-touching class built under `application/**` instead of injected, and `FsPortBypass` flags a raw write that goes around the port.
- **Replicates.** `--replicates N` (N > 1) with one or more problem ids runs N seeds — `seed = replicate index` — and reports mean ± stddev across them. Every other flag (cost cap, security tests, cache configuration, fixer passes, infrastructure mode) is carried into each replicate; only the seed varies, and several problems can be replicated in one invocation. `replicate_summary.json` + `replicate_summary.md` are written into the first replicate's run directory, so the summary sits with the runs it summarizes. A failing replicate is isolated rather than fatal: it is recorded as `"replicate <N>: <ErrorType>: <message>"` in the summary's `failures`, excluded from the aggregated statistics, and reported in the Markdown as a count of replicates that failed — the surviving replicates still produce a summary. `BudgetExceededError` and `ReplayCacheMissError` remain the deliberate exceptions and abort the whole calibration, being infrastructure signals rather than results; when no replicate produces a result at all, the run raises `ReplicateCalibrationError` (a `RuntimeError`) naming the problem id and every failure.
- **Pattern-vocabulary ablation.** `--architect-mode {patterned,free}` (default `patterned`) controls how the RequirementCompiler annotates the classes it emits. Under `free` every class is assigned the `SimpleClass` pattern instead of a GoF/DDD one; the module decomposition, the class granularity and the invariants are identical, and only the pattern annotation is fixed. It is the control arm for measuring what the pattern vocabulary itself contributes — run the same problem both ways and compare.
- **Claims policy.** Accepting a fix, declaring a regression, or updating a baseline requires N ≥ 3 replicates; below that a run is exploratory, and the output says so — `replicate_summary.md` carries a below-threshold note, and a single-sample sweep labels itself exploratory in its SUMMARY.md.
- **Regression gate.** Every sweep judges each problem against that problem's stored golden baseline and writes a verdict per problem into SUMMARY.md under "Regression Gate (vs routing-stamped goldens)" — `no golden (uncalibrated)`, `not comparable (routing changed since calibration)`, `OK`, or `REGRESSION` at a drop of 2σ or more below the baseline mean. Only the last gates; when a metric trips, `regressions.json` is written into the run directory. Each verdict is also emitted as a `regression_gate` log event.
- **Measurement honesty.** An unmeasured metric is never reported as `0.0`. `test_outcome.security_tests_pass` serializes as JSON `null` when no security tests were collected and renders `n/a` in Markdown; `test_outcome.tests_pass` / `test_outcome.functional_tests_pass` serialize as `null` when `test_outcome.test_status` is "not measured" with zero tests collected. A genuine 0% still reports `0.00`, so a reader can tell "insecure" from "security tests not enabled". Architecture violations render as `<n> ⚠` when non-zero.
- **Report schema.** `eval_report.json` and `metrics.json` carry `"schema_version": 2` and group the metrics into seven nested objects — `test_outcome`, `cost`, `velocity`, `structure`, `reliability`, `notation` and `security_scan` — mirroring the value objects that compose `EvalMetrics` (`squeaky_clean/application/evaluation/eval/metrics/model/`, alongside `SecurityScanStats` in `squeaky_clean/domain/value_objects/metrics/`). `architecture_violations`, `total_wall_clock_ms`, the parallelism and cache fields, `replicate_id`, `runs` and `budget_exceeded` stay at the top level. Reports written under the earlier flat, unversioned schema are still read: the metrics-history aggregator and the `scripts/comparison/` and `scripts/comparison_v2/` benchmark scripts flatten nested payloads back to the historical leaf names, so old and new runs yield identical keys and historical runs stay comparable.
- **Notation novelty.** `EvalMetrics.notation.notation_novelty` counts the architect-emitted Squib class constructions whose *shape* — the pattern name plus which of `fields`, `methods`, `depends`, `concretes`, `implements` and `invariants` the class declares — appears nowhere in the `.squib` fixture corpus at `eval/squib_fixtures/`. It is observational, reported in every run's `eval_report.json` under the `notation` group, and never gates. `notation_novelty.json` lands beside the emitted notation in the problem-set directory, and a non-zero count also copies the raw notation into `<results-root>/notation-triage/`, so a new architect shape is adopted into the fixture corpus deliberately rather than met first in production as a downstream contract break. That harvest is best-effort — a failed write leaves the run unaffected and the sidecar still records the count — but the failure is logged as `notation_triage_write_failed`. `NotationNoveltyReporter` (`squeaky_clean/application/evaluation/eval/run/notation_novelty_reporter.py`) over `NotationShapeClassifier` (`squeaky_clean/application/generation/notation/notation_shape_classifier.py`); see [`squib.md`](squib.md).
- **Run manifest.** `manifest.json` records what a run ran under: the per-tier model identifiers resolved by the router, the framework SHA, the spec-library version and hashes, the replicate id, and `toolchains` — the first version line reported by `node`, `npm`, `javac`, `mvn`, `go` and `cargo`, and `absent` for any tool not on `PATH` (also `absent` when the probe errors or exceeds its five-second timeout). Scores depend on those versions — a Node major version, or a JDK that rejects language features a newer one accepts, changes results — so a manifest attributes a score to the environment that produced it. `RunManifest` reads both through domain ports, `GitInfo` and `ToolchainInfo` (`squeaky_clean/domain/interfaces/provenance/`), whose subprocess adapters `GitInfoAdapter` and `ToolchainProbeAdapter` (`squeaky_clean/infrastructure/observability/`) are injected by the composition root. Left unwired the manifest degrades to `framework_sha: "unknown"` and an empty `toolchains` map rather than failing the run.
- **Per-agent eval.** `eval/per_agent/fixtures/` + scoring functions per agent class for unit-eval (decoupled from full pipeline).
- **Routing fixtures.** `eval/squib_fixtures/` — one minimal Squib per catalog pattern not already required by a benchmark ProblemSpec, listed in `manifest.json` and generated by `scripts/gen_squib_fixtures.py`, parsed through the real parse → assign path in all four languages to assert each pattern reaches its own dedicated emitter rather than the `SimpleClass` escape hatch. Deterministic; no LLM calls.
- **Peer-shape fixtures.** `eval/squib_fixtures/*_depends_shape.squib` — one hand-authored Squib per polymorphic pattern family, expressing the abstract/concrete split in the peer shape (each concrete `depends:` on the abstract, no class declares `concretes:`), so the normalizer's role inference and the peer shape's emission are pinned. Hand-maintained: not listed in `manifest.json`, not produced by the generator, and not part of routing coverage.
- **Micro-evals.** `--micro-evals` runs a pattern × language matrix over every `*.squib` in that directory, routing and peer-shape fixtures alike — the middle tier between unit tests, which stop at the LLM seam, and full benchmark problems. Each fixture module's classes are emitted through the real model routing and the real pattern emitters, then compiled, once per target language (Python, Java, TypeScript). See [Micro-eval matrix](#micro-eval-matrix).
- **Dashboard.** `--rebuild-dashboard` aggregates `meta-evaluation-results/` history into a static HTML chart.

## Micro-eval matrix

`--micro-evals` verifies that a pattern's emitters produce *compiling* code in a language, at the cost of a handful of LLM calls plus one compiler invocation per cell. For every squib fixture in `eval/squib_fixtures/` (`*.squib` — every file in the directory, not only the routing fixtures listed in `manifest.json`) it emits that fixture module's classes through the real model routing and the real pattern emitters, then compiles the result — once per target language. All sibling classes of the fixture module are emitted together, so cross-class contracts (`implements` / `extends`) are exercised, not just single-file syntax. Each fixture is self-contained: every type its focal class references — parameter, return and field types, and the entries of `concretes:` — is declared as a sibling and emitted with it, so a cell's compile never depends on a type the module never declared. Those siblings declare real fields, method signatures, invariants and concretes rather than placeholder stubs, so the cells exercise genuine cross-class contracts.

Cells are isolated: a failure or an exception in one cell fails only that cell, and a language with no compiler or implementer registered fails the cell loudly rather than being silently skipped.

| Language | Compile gate |
|---|---|
| Python | No ahead-of-time compile step exists, so the gate parses every `.py` file — which still catches truncated emissions, stray prose and malformed definitions. |
| Java | The JDK's `javac` directly against every `.java` file in the cell: no Maven and no `pom.xml`, an order of magnitude faster than `mvn`. 60-second timeout; class output under `_out/`. |
| TypeScript | The TypeScript compiler, with `tsconfig.json` (ES2022, nodenext modules, strict, noEmit, esModuleInterop, skipLibCheck, `include: ["src/**/*.ts"]`) and `package.json` (`{"type": "module"}`) scaffolded into each cell, mirroring what the integration bootstrap generates for full runs. |

Java cells promote the ICP tier to the manager model — the small model misses Java contracts often enough to matter — mirroring the per-problem recipe.

Cells are written under `<run-dir>/micro-evals/<pattern>-<language>/`, and `micro_eval_report.md` + `micro_eval_report.json` land in the run directory. The Markdown report is a pattern × language pass matrix (`✅` / `❌` with the compile-error count, `—` where a cell has no adapter) with header counts of cells / passed / failed / total cost, plus a Failures section listing `pattern/language`, the error count and a compiler-output excerpt. The command prints its result and exits:

```
[squeaky] micro-evals: <passed>/<total> cells passed, $<cost> — <report path>
```

`--micro-patterns <prefix>[,<prefix>...]` narrows the matrix: only fixtures whose filename stem starts with one of the comma-separated prefixes are run, and the default — empty — runs every fixture as before. It modifies `--micro-evals` rather than being a command of its own. The match is on the stem, so `--micro-patterns state` takes `state.squib` and `state_depends_shape.squib` together, and `squeaky --micro-evals --micro-patterns strategy,visitor` iterates on one pattern's emitters without paying for the full fixture × language matrix.

`--micro-evals` is one of the accepted top-level commands: the CLI requires exactly one of `--problem`, `--problems`, `--sweep`, `--problem-file`, `--recover-from`, `--triage`, `--refactor`, `--squib-file`, `--rebuild-dashboard`, `--micro-evals`, or `--resume`.

Running the Java and TypeScript gates locally needs a JDK and Node.js on `PATH`; CI pins Temurin JDK 21 and Node.js 20 so neither gate floats with the runner image.

## See also

- [`overview.md`](overview.md) — 5-min pitch
- [`squib.md`](squib.md) — Squib grammar reference
- [`writing_a_problem_spec.md`](writing_a_problem_spec.md) — author's guide
- [`extending.md`](extending.md) — custom-pattern hook + custom Tier C agents
- [`architecture_recovery.md`](architecture_recovery.md) — the inverse (brownfield → Clean Architecture) pipeline
- [`infrastructure_layer_design.md`](infrastructure_layer_design.md) — full Tier C design
- [`BENCHMARK_METHODOLOGY.md`](../BENCHMARK_METHODOLOGY.md) — replication policy, golden baselines, ACS
