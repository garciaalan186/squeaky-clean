# Extending Squeaky Clean

Two extension hooks for users who need patterns or technologies the bundled catalog doesn't cover.

## Custom patterns (Milestone F4)

Add domain-specific patterns (event-sourcing aggregate, CQRS handler, saga, etc.) without modifying the framework core.

### 1. Author your custom ICP

Write a Markdown spec at any path on your filesystem. Mirror the structure of `squeaky_clean/interface/agent_specs/icps/python/ddd_clean/EntityICP.md` (Identity / Model Tier / Input Contract / Output Contract / Constraints / Pattern Knowledge / Failure Modes).

```
~/my_specs/icps/python/custom/EventSourcedAggregateICP.md
```

### 2. Author a custom-pattern manifest

```json
// ~/my_specs/manifest.json
{
  "patterns": [
    {
      "name": "EventSourcedAggregate",
      "icp_spec_name": "python/custom/EventSourcedAggregateICP"
    }
  ],
  "extra_spec_roots": ["~/my_specs/"]
}
```

`name` matches the Squib `pattern` field the architect emits. `icp_spec_name` is the spec lookup key. `extra_spec_roots` is the directory the framework's `LoadAgentSpec` searches IN ADDITION to its bundled library.

### 3. Run with the manifest

```bash
squeaky generate \
    --problem-file my_problem.json \
    --custom-patterns ~/my_specs/manifest.json \
    --infra=auto
```

When the architect produces `MyAggregate -> EventSourcedAggregate`, the framework routes to your custom ICP. The bundled library still resolves all other patterns (Entity, ValueObject, ...).

See `eval/custom_patterns/example_event_sourced_aggregate.json` + the matching `EventSourcedAggregateICP.md` for a worked example.

## Custom Tier C technologies (Milestone H)

Add technology snapshots beyond the bundled catalog. The framework's `TechSpecResolver` walks four sources in priority order: bundled snapshot → cache → MCP → web fetch. The first three are extension points.

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

Validate against the schema before shipping:

```bash
python -c "from src.infrastructure.techspec.jsonschema_techspec_validator import JSONSchemaTechSpecValidator; from pathlib import Path; print(JSONSchemaTechSpecValidator(Path('eval/tech_specs/_schema.v1.json')).validate(__import__('json').loads(Path('your-spec.json').read_text())))"
```

### Configure a private MCP server

Set `CLEAN_AGENT_TECHSPEC_MCP_URL` in your environment to point at an internal docs aggregator. The framework's `MCPTechDocFetcher` adapter queries it before falling through to live web fetch.

```bash
export CLEAN_AGENT_TECHSPEC_MCP_URL=https://docs.internal.example.com/techspecs
squeaky generate ...
```

The MCP must respond with JSON conforming to the TechSpec schema. The sanitizer + validator pipeline still runs on every fetched response.

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

## Custom languages

The framework's `LanguageAdapterRegistry` is registry-driven (Milestone K9). Adding a new language requires:

1. Add a `TargetLanguage` enum value.
2. Provide six adapters: ICP-spec library, integration bootstrap, granularity rule, test runner, dependency installer, implemented-class parser.
3. Provide a `ProblemSpecFormatter` extension if the language has unusual identifier conventions (e.g. PowerShell verb-noun).
4. Register everything in `language_adapter_registry.py`'s `REGISTRY` dict.
5. Run `pytest tests/interface/cli/test_language_adapter_registry_coverage.py` — it asserts every enum value has a registered factory.

This is a substantial body of work (~2000 lines for a new language at full Tier C parity); we recommend opening an RFC issue first.

## Recovery language extractors

Adding a language to **Architecture Recovery** (the brownfield-ingest inverse pipeline) is much lighter than full generation parity, because everything after ingest is language-neutral. You only implement one thing: a `ClassCatalogExtractor`.

1. Implement `ClassCatalogExtractor.extract(root) -> ClassCatalog` in `squeaky_clean/application/use_cases/recovery/`. Python uses a real `ast` walk; Java/JS/TS subclass `RegexCatalogExtractor` and reuse `RegexClassParser` + `RegexDecoratorScanner`, providing the class/method/field regexes and the FQN scheme.
2. Register it in `class_catalog_extractor_factory.py` under its `TargetLanguage`.
3. If the language has test/build conventions not already covered, extend `IngestScope`.

The extractor's job is to emit `ClassRecord`s (FQN, bases, methods, fields, imports, decorators); layer assignment, pattern classification, decomposition, violation analysis, and refactoring are all shared and unchanged. See [`architecture_recovery.md`](architecture_recovery.md).

## See also

- [`architecture.md`](architecture.md) — three model tiers
- [`architecture_recovery.md`](architecture_recovery.md) — the inverse recovery pipeline
- [`infrastructure_layer_design.md`](infrastructure_layer_design.md) — full Tier C / Tier T / Tier B design
