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

This routes the matching classes to **Tier C ICPs** which generate adapter code with real SDK calls (not stubs). Without explicit choices, you can opt into MCDA-driven selection with `--infer-infrastructure`, but this is exploratory; real production specs declare.

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

The framework's contract registry persists the producer's declaration on disk. The consumer's run resolves it and validates that the consumer's `ConsumedEvent` entity carries the same field names verbatim — case-tolerant across language boundaries (Java's `receivedAt` matches Python's `received_at`).

### 6. Mark sensitive fields with `data_classification`

```json
"data_classification": [
  {"field_ref": "User.password_hash", "sensitivity": "credential"},
  {"field_ref": "Session.token", "sensitivity": "session_token"}
]
```

Sensitivity tags ground the SecurityArchitect's concern generation in declared sensitivity rather than name-guessing. Fields tagged `credential` cannot be exposed via getters; `session_token` fields are stored opaquely.

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

1. Read `eval_report.json` for `tests_pass`, `architecture_violations`, `cross_module_dependency_violations`, `http_convention_violations`. Most violations are caught + retried automatically; persistent violations are logged + cause graceful exit.
2. Read `architecture.squib` to see what the architect produced. If a class belongs to the wrong module, your `required_bounded_contexts` may be too coarse; split.
3. Use `--deterministic` to lock down stochastic variation and isolate spec-induced issues.
4. Use `--replicates 5` to surface mean ± stddev of `tests_pass` if you suspect stochastic drift.

## Worked example: Twitter clone

Spec is at `examples/twitter_clone/twitter_problem.json`. Notable decisions:

- `required_bounded_contexts: ["Auth", "Posts", "Timeline"]` — three contexts, the architect produces ~6-9 modules across them.
- `domain_conventions: ["timeline_includes_self", "follow_asymmetric"]` — without these, the architect would produce a "tweets-by-followees only" timeline that excludes the user's own posts (real Twitter includes them).
- `query_semantics: [{"use_case": "GetTimelineUseCase", "shape": "self_plus_followees"}]` — the architect picks a `find_by_authors([self_id, ...followee_ids])` repository method.
- `data_classification: [{"field_ref": "User.password_hash", "sensitivity": "credential"}]` — SecurityArchitect's concerns ground here.

Cost: ~$0.40. ACS ≈ 16. Yields a working Flask app with port/adapter discipline preserved.

## See also

- [`overview.md`](overview.md) — what the framework does
- [`architecture.md`](architecture.md) — the three model tiers
- [`squib.md`](squib.md) — Squib grammar reference
- [`extending.md`](extending.md) — custom-pattern hooks
- `examples/` — three runnable sample ProblemSpecs
