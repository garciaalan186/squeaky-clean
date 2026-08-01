# Extending Squeaky Clean

Two extension hooks for users who need patterns or technologies the bundled catalog doesn't cover. The bundled pattern catalog is the full 34-pattern GoF + DDD/Clean set in all four languages; the custom-pattern hook is for domain-specific patterns beyond it.

## Custom patterns (Milestone F4)

Add domain-specific patterns (event-sourcing aggregate, CQRS handler, saga, etc.) without modifying the framework core.

### 1. Author your custom emitter

Write a Markdown spec at any path on your filesystem. Mirror the structure of `squeaky_clean/interface/agent_specs/emitters/python/ddd_clean/EntityEmitter.md` (Identity / Model Tier / Input Contract / Output Contract / Constraints / Pattern Knowledge / Failure Modes).

```
~/my_specs/emitters/python/custom/EventSourcedAggregateEmitter.md
```

### 2. Author a custom-pattern manifest

```json
// ~/my_specs/manifest.json
{
  "patterns": [
    {
      "name": "EventSourcedAggregate",
      "emitter_spec_name": "python/custom/EventSourcedAggregateEmitter"
    }
  ],
  "extra_spec_roots": ["~/my_specs/"]
}
```

`name` matches the Squib `pattern` field the architect emits. `emitter_spec_name` is the spec lookup key, resolved under `<extra_spec_root>/emitters/<lang>/<category>/<Name>Emitter.md`. `extra_spec_roots` is the directory the framework's `LoadAgentSpec` searches IN ADDITION to its bundled library.

### 3. Run with the manifest

```bash
squeaky generate \
    --problem-file my_problem.json \
    --custom-patterns ~/my_specs/manifest.json \
    --infra=auto
```

When the architect produces `MyAggregate -> EventSourcedAggregate`, the framework routes to your custom emitter. The bundled library still resolves every other pattern to its own dedicated emitter — all 34 recognized patterns are covered in each of the four languages, so a custom manifest is only needed for patterns outside that catalog.

A custom pattern is by definition a name the catalog doesn't hold, which is also what `ProblemSpec.required_patterns` validates against: list only catalog names there, and let the manifest carry the custom ones. A name neither the catalog nor a manifest recognizes still falls through to the `SimpleClass` escape hatch rather than aborting the run.

See `eval/custom_patterns/example_event_sourced_aggregate.json` + the matching `eval/custom_patterns/specs/emitters/python/custom/EventSourcedAggregateEmitter.md` for a worked example.

## Custom Tier C technologies (Milestone H)

Add technology snapshots beyond the bundled catalog. The framework's `TechSpecResolver` walks its sources in priority order: bundled snapshot → fresh cache → MCP → web fetch → a stale-tolerant cache entry inside the grace window → fail. The first three are extension points. Every source that fails emits a structured JSON run-log event carrying its reason, and if nothing resolves the run fails with `TechSpecResolutionError` carrying one reason per source it tried — so a snapshot you added that the framework then declined is visible rather than silently skipped.

### Add a bundled snapshot

Drop a JSON file at `eval/tech_specs/<category>/<technology>/<version>.json` matching the schema at `eval/tech_specs/_schema.v1.json`:

```json
{
  "schema_version": "v1",
  "category": "kv_cache",
  "technology": "valkey",
  "version_pin": "valkey-py==1.0",
  "language": "python",
  "install": {"manager": "pip", "package": "valkey-py==1.0"},
  "imports": {
    "primary": "import valkey",
    "types": ["from valkey.exceptions import ValkeyError"]
  },
  "client_construction": {
    "code": "self._client = valkey.Valkey(host=host)",
    "thread_safe": true,
    "dependencies": ["VALKEY_HOST"]
  },
  "primary_operations": [
    {
      "name": "set",
      "signature": "(key: str, value: str) -> None",
      "sdk_call": "self._client.set(key, value)",
      "error_types": ["ValkeyError"],
      "idempotency": "idempotent"
    }
  ],
  "auth": {"method": "env_credentials", "env_vars": ["VALKEY_HOST"]}
}
```

A snapshot that is unreadable, is not a JSON object, fails schema validation, or is rejected by the builder is logged as a `techspec_snapshot_rejected` event naming the path and the reason, and the resolver falls through to the next source. Validate against the schema before shipping:

```bash
python -c "from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import JSONSchemaTechSpecValidator; from pathlib import Path; print(JSONSchemaTechSpecValidator(Path('eval/tech_specs/_schema.v1.json')).validate(__import__('json').loads(Path('your-spec.json').read_text())))"
```

### Configure a private MCP server

Set `CLEAN_AGENT_TECHSPEC_MCP_URL` in your environment to point at an internal docs aggregator. The framework's `MCPTechDocFetcher` adapter queries it before falling through to live web fetch.

```bash
export CLEAN_AGENT_TECHSPEC_MCP_URL=https://docs.internal.example.com/techspecs
squeaky generate ...
```

The MCP must respond with JSON conforming to the TechSpec schema. The sanitizer + validator pipeline still runs on every fetched response, and a rejected response is logged as a `techspec_source_failed` event naming `mcp` and the reason before the resolver falls through.

### Add a custom MCDA scoring entry

If you want `--infer-infrastructure` to consider your custom technology, add it to `eval/mcda_scores/<category>.json`:

```json
{
  "category": "kv_cache",
  "candidates": [
    {"technology": "redis", "version_pin": "redis-py==5.0", "scores": {"ops": 4, "cost": 4, ...}, "stability": "ga"},
    {"technology": "valkey", "version_pin": "valkey-py==1.0", "scores": {"ops": 4, "cost": 4, ...}, "stability": "beta"}
  ]
}
```

Scores 1–5 across 8 criteria (ops, cost, cold, thru, eco, reg, lic, team). Stability tier is `ga | beta | preview` for the tie-breaker.

## Pattern emitter spec shapes

A bundled pattern emitter is authored in one of two shapes, and both resolve through the same lookup.

| Shape | Where it lives |
|---|---|
| Per-language | One complete spec per language at `squeaky_clean/interface/agent_specs/emitters/<language>/<category>/<Pattern>Emitter.md`. The 11 DDD/Clean patterns ship this way — 44 files. |
| Shared template | One cross-language template at `emitters/_shared/<category>/<Pattern>Emitter.md`, composed at emission time with the language profile at `emitters/_shared/profiles/<language>.md`. Profiles ship for `python`, `javascript`, `typescript` and `java`. All 23 creational, structural and behavioral patterns ship this way. |

Resolution prefers the shared template and falls back to the per-language file, so a pattern not yet cut over behaves exactly as before; a shared template with no matching language profile raises rather than degrading silently.

For a pattern authored as a shared template:

- A language-specific fix goes in that language's profile block.
- A change to the shared contract goes in the single template, so it lands in all four languages at once and needs validating across them.
- Adding a language means adding its profile, not cloning the spec.
- The drift guards — for example the Java §Notation `float` → `double` type-fidelity rule — are asserted once per pattern against the composed template + profile, parameterized over every shared-template pattern, rather than against four file copies.

A template pulls a named block in with `{{profile:<block_name>}}` and gates lines on language with a flat, non-nesting `{{#lang:java}}` … `{{/lang}}` block whose opener accepts a comma list. Full grammar and the shipped block names: [`architecture.md`](architecture.md#emitter-spec-composition).

## Custom languages

The framework's `LanguageAdapterRegistry` is the single per-language dispatch table (Milestone K9): the adapter selector, the compiler factory and the test-runner factory are all thin views over it, so a language is added in one place. Adding a new language requires:

1. Add a `TargetLanguage` enum value.
2. Provide the emitter-spec library for the language — a spec file for each of the 11 DDD/Clean patterns authored per language, under `emitters/<language>/ddd_clean/`, plus one profile at `emitters/_shared/profiles/<language>.md` supplying the delta blocks for all 23 creational, structural and behavioral patterns, which are authored once as shared cross-language templates.
3. Provide a `ProblemSpecFormatter` extension if the language has unusual identifier conventions (e.g. PowerShell verb-noun).
4. Add one `LanguageAdapterEntry` to `language_adapter_registry.py`'s `REGISTRY` dict, carrying the test-runner factory (it takes an exclude glob, `None` meaning run everything, plus the composition root's `RunLogger`, `None` meaning a silent null logger) plus the language's functional-test exclude pattern, the granularity rule, the integration bootstrap, the implemented-class parser, the dependency installer (it takes the same logger, so a failed install lands in the structured JSON run log), and — only if the language has a meaningful ahead-of-time compile/typecheck step — a compiler. TypeScript and Java declare one; Python, JavaScript, Go and Rust leave it `None`.
5. Run `pytest tests/interface/cli/test_language_adapter_registry_coverage.py` — it asserts every enum value has a registered entry.

This is a substantial body of work (~2000 lines for a new language at full Tier C parity); we recommend opening an RFC issue first.

## Recovery language extractors

Adding a language to **Architecture Recovery** (the brownfield-ingest inverse pipeline) is much lighter than full generation parity, because everything after ingest is language-neutral. You only implement one thing: a `ClassCatalogExtractor`.

1. Implement `ClassCatalogExtractor.extract(root) -> ClassCatalog` in `squeaky_clean/application/generation/recovery/extraction/`. Python uses a real `ast` walk; Java/JS/TS subclass `RegexCatalogExtractor` and reuse `RegexClassParser` + `RegexDecoratorScanner`, providing the class/method/field regexes and the FQN scheme.
2. Register it in `class_catalog_extractor_factory.py` under its `TargetLanguage`.
3. If the language has test/build conventions not already covered, extend `IngestScope`.

The extractor's job is to emit `ClassRecord`s (FQN, bases, methods, fields, imports, decorators); layer assignment, pattern classification, decomposition, violation analysis, and refactoring are all shared and unchanged. See [`architecture_recovery.md`](architecture_recovery.md).

## See also

- [`architecture.md`](architecture.md) — three model tiers
- [`architecture_recovery.md`](architecture_recovery.md) — the inverse recovery pipeline
- [`infrastructure_layer_design.md`](infrastructure_layer_design.md) — full Tier C / Tier T / Tier B design
