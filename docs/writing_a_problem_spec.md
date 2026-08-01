# Writing a ProblemSpec

A walkthrough + best practices for authoring a `ProblemSpec` JSON.

## The minimum viable spec

```json
{
  "id": "MY_APP",
  "tier": 1,
  "slug": "my_app",
  "description": "One paragraph: what this service does, who consumes it, what bounded contexts it spans.",
  "required_bounded_contexts": ["ContextA", "ContextB"],
  "acceptance_criteria": [
    "Given <input>, When <verb> is called, Then result is <output>",
    "Given <bad input>, When <verb> is called, Then an error is raised"
  ],
  "expected_module_count": [2, 4],
  "expected_class_count": [8, 16],
  "required_patterns": ["Entity", "ValueObject", "UseCase", "Repository"],
  "target_language": "python"
}
```

Six required fields: `id`, `description`, `acceptance_criteria`, `required_patterns`, `target_language`, plus `tier` + `slug` for the eval-harness-friendly file path.

`required_patterns` is checked against the 34-name pattern catalog as the spec is loaded, so a typo or an invented name fails immediately with `ValueError: unknown pattern: '<name>'` rather than being accepted and quietly ignored. Domain-specific patterns outside the catalog are supplied through the custom-pattern registry (see [`extending.md`](extending.md)) instead of being listed here; a name the framework doesn't recognize appearing in a generated architecture still routes to the `SimpleClass` escape hatch rather than aborting the run.

## Two halves: behavior and structure

The JSON above is flat, and stays that way — flat fields are the construction surface. In code, a `ProblemSpec` exposes two read-only views over them:

- **`.behavior`** → `BehaviorSpec`: `acceptance_criteria`, `produces_contracts`, `consumes_contracts`, `data_classification`, `expected_outcomes`. This is the acceptance oracle — the part of the problem a Squib cannot express, and what the OracleCompiler compiles tests from. Always yours to author.
- **`.structural_hints`** → `StructuralHints`: `required_patterns`, `required_bounded_contexts`, `expected_module_count`, `expected_class_count`. This is the half a Squib already encodes.

The practical consequence: on the greenfield path the structural fields are *hints* to the architect, so treat them as guardrails rather than targets (see the anti-patterns table). On the squib-first (`--squib-file`) and recovery paths the architecture already exists, so the same values are derived from it by `derive_structural_hints_from_squib` — deterministic, no LLM call — and only the behavioral half needs supplying.

## Best practices

### 1. Acceptance criteria are Gherkin-shaped

Every criterion is `Given <state>, When <verb> is called, Then <expectation>`. The verb is what the architect uses to decide which class owns the method.

- **Good**: `"Given a user 'alice' and password 'pw1234567', When sign_up is called, Then result is a User"` — `sign_up` becomes a method on a class.
- **Bad**: `"The user can sign up"` — no verb, no expectation, architect can't generate tests.
- **Bad**: `"sign_up('alice', 'pw1234567') returns a User"` — too implementation-specific; architect should choose argument shapes.

### 2. Use `required_bounded_contexts` to drive module decomposition

The architect uses these names verbatim as MODULE names. Pick names that map to single-responsibility business concepts: `Auth`, `Posts`, `Timeline`, `Inventory`, `Billing`. Avoid `Database`, `API`, `Logic` — those are layers, not contexts.

### 3. Declare `infrastructure_choices` whenever you know the SDK

If you know your service uses Kafka + S3, declare it:

```json
"infrastructure_choices": [
  {"category": "message_queue_producer", "technology": "kafka", "version_pin": "confluent-kafka==2.5"},
  {"category": "blob_storage", "technology": "s3", "version_pin": "boto3==1.34"}
]
```

This routes the matching classes to **Tier C emitters** which generate adapter code with real SDK calls (not stubs). Without explicit choices, you can opt into MCDA-driven selection with `--infer-infrastructure`, but this is exploratory; real production specs declare.

### 4. Use `domain_conventions` to encode common semantics

Common social/e-commerce/auth semantics often have to be re-derived in every Gherkin criterion or get silently dropped. Use the convention registry:

```json
"domain_conventions": ["timeline_includes_self", "follow_asymmetric", "auth_session_single_active"]
```

Each tag maps (in `convention_to_invariant.py`) to a Squib INVARIANT the architect MUST surface verbatim. Today's registry covers ~9 common conventions; PRs welcome to add more.

### 5. Cross-service contracts via `produces_contracts` / `consumes_contracts`

If you're authoring a multi-service distributed system, declare contracts:

**Producer service:**
```json
"produces_contracts": [{
  "name": "events.raw",
  "transport": "kafka:events.raw",
  "fields": [
    {"name": "id", "type": "str"},
    {"name": "received_at", "type": "str"},
    {"name": "headers", "type": "dict[str, str]"},
    {"name": "payload", "type": "str"}
  ]
}]
```

**Consumer service:**
```json
"consumes_contracts": [{"contract_name": "events.raw", "role": "consumes"}]
```

The framework's contract registry persists the producer's declaration on disk. The consumer's run resolves it and validates that the consumer's `ConsumedEvent` DTO carries the same field names verbatim — case-tolerant across language boundaries (Java's `receivedAt` matches Python's `received_at`).

### 6. Mark sensitive fields with `data_classification`

```json
"data_classification": [
  {"field_ref": "User.password_hash", "sensitivity": "credential"},
  {"field_ref": "Session.token", "sensitivity": "session_token"}
]
```

Sensitivity tags ground the ThreatAnalyzer's concern generation in declared sensitivity rather than name-guessing. Fields tagged `credential` cannot be exposed via getters; `session_token` fields are stored opaquely.

### 7. Attach `golden_metrics` once the spec is calibrated

`golden_metrics: GoldenMetrics | None` is the optional calibrated baseline a spec's runs are judged against. Leave it `None` — the default — and the problem is uncalibrated: the regression gate reports `no golden (uncalibrated)` and never gates.

`GoldenMetrics` is a frozen value object carrying `replicates`; the mean and stddev of `tests_pass`, `functional_pass`, `security_pass` and `cost_usd`; `model_routing`, a tuple of `"<tier>=<model>"` entries for architect / manager / icp / fixer recording what the calibration ran under; and `calibrated_run`, the run directory name it came from. Wall-clock and cache figures are not calibrated and do not gate.

Calibrate at N ≥ 3 (`--replicates 3`) and take the means and σ from the resulting `replicate_summary.json`. A replicate that fails is recorded in that file's `failures` array and excluded from the statistics rather than aborting the calibration, so the surviving replicates still yield a summary — check the count before treating the means as an N = 3 baseline. The routing stamp is what keeps a model bump from reading as a tool regression: when the current routing differs from the calibration routing, the gate reports `not comparable (routing changed since calibration)` instead of failing the run. See [`BENCHMARK_METHODOLOGY.md`](../BENCHMARK_METHODOLOGY.md) for the gate's verdicts and the published baselines.

## Anti-patterns

| Don't | Do |
|---|---|
| Use criteria like `"The system handles errors gracefully"` | `"Given an empty body, When parse is called, Then an error is raised"` |
| Combine multiple verbs in one criterion | One criterion per verb-shaped behavior |
| Specify implementation details (SQL, JSON parsing inline) | Specify behavior contracts; let the architect decompose |
| Set `expected_class_count: [50, 100]` for a Calculator | Let the count match the actual decomposition; over-specifying triggers verb-not-in-spec stubs |
| Use `expected_module_count: [1, 1]` for distributed systems | Multi-context problems span 4–9 modules |
| Forget `target_language` | Required; the framework can't infer it |

## Iterating

If a generated run looks wrong:

1. Read `eval_report.json` for `test_outcome.tests_pass`, `architecture_violations`, `notation.cross_module_dependency_violations`, `notation.http_convention_violations`. The report carries `"schema_version": 2` and groups its metrics into seven nested objects — `test_outcome`, `cost`, `velocity`, `structure`, `reliability`, `notation`, `security_scan` — with `architecture_violations`, `total_wall_clock_ms`, the parallelism and cache fields, `replicate_id`, `runs` and `budget_exceeded` at the top level. Most violations are caught + retried automatically; persistent violations are logged + cause graceful exit. A metric reported as `null` (or `n/a` in Markdown) was not measured — it is not a zero score.
2. Read `architecture.squib` to see what the architect produced. If a class belongs to the wrong module, your `required_bounded_contexts` may be too coarse; split.
3. Use `--deterministic` to lock down stochastic variation and isolate spec-induced issues.
4. Use `--replicates 5` to surface mean ± stddev of `tests_pass` if you suspect stochastic drift; read `replicate_summary.md` in the first replicate's run directory. A single run is exploratory — concluding that a change helped or hurt takes N ≥ 3.

## Worked example: Twitter clone

Spec is at `examples/twitter_clone/twitter_problem.json`. Notable decisions:

- `required_bounded_contexts: ["Auth", "Posts", "Timeline"]` — three contexts, the architect produces ~6-9 modules across them.
- `domain_conventions: ["timeline_includes_self", "follow_asymmetric"]` — without these, the architect would produce a "tweets-by-followees only" timeline that excludes the user's own posts (real Twitter includes them).
- `query_semantics: [{"use_case": "GetTimelineUseCase", "shape": "self_plus_followees"}]` — the architect picks a `find_by_authors([self_id, ...followee_ids])` repository method.
- `data_classification: [{"field_ref": "User.password_hash", "sensitivity": "credential"}]` — the ThreatAnalyzer's concerns ground here.

Cost: ~$0.40. ACS ≈ 16. Yields a working Flask app with port/adapter discipline preserved.

## See also

- [`overview.md`](overview.md) — what the framework does
- [`architecture.md`](architecture.md) — the three model tiers
- [`squib.md`](squib.md) — Squib grammar reference
- [`extending.md`](extending.md) — custom-pattern hooks
- `examples/` — three runnable sample ProblemSpecs
- `eval/problems/` — the built-in benchmark specs (`P0`–`P11`), selectable by id with `--problem` / `--problems`. `p6_stock_monitor` (Observer), `p7_order_lifecycle` (State), `p8_text_editor` (Command + Memento), `p9_drawing_canvas` (Composite + Visitor), `p10_report_builder` (Builder + AbstractFactory + Prototype) and `p11_notification_middleware` (ChainOfResponsibility + Decorator + Adapter + Facade) are compact specs whose criteria pin one pattern family each — useful templates when the behaviour you're specifying is pattern-shaped.
