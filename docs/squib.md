# Squib — Grammar Reference

Squib is the compact text format the PrincipalArchitect emits and ICPs consume. It is the framework's instruction set architecture.

## Top-level structure

A run produces one or more `MODULE` blocks, separated by blank lines:

```
MODULE <ModuleName>
LAYER <Domain|Application|Infrastructure|Interface>
EXPORTS [<ClassName>, ...]
DEPENDS [<Module>::<Type>, ...]
CLASSES {
  <ClassName> -> <PatternName> {
    fields:     [<name: Type>, ...]
    methods:    [<methodName(arg: Type): Return>, ...]
    depends:    [<ClassName | Module::ClassName>, ...]
    concretes:  [<ClassName>, ...]
    invariants: [<free-text rule>, ...]
  }
}
INVARIANTS [<free-text module-level rule>, ...]
```

## Field types

| Field | Required | Notes |
|---|---|---|
| `MODULE <Name>` | Yes | PascalCase, globally unique within the architecture |
| `LAYER <Domain\|Application\|Infrastructure\|Interface>` | Yes | Each name is fixed; per-language file layout derived from it |
| `EXPORTS [...]` | Yes (may be empty) | Classes other modules can `DEPENDS` on |
| `DEPENDS [...]` | Yes (may be empty) | Required for cross-module class dependencies (validated DAG) |
| `CLASSES { ... }` | Yes | One or more class definitions |
| `INVARIANTS [...]` | Yes (may be empty) | Module-level invariants surfaced to all ICPs in this module |

## Class definitions

| Field | Required | Notes |
|---|---|---|
| `<ClassName> -> <PatternName>` | Yes | PatternName from the 34-pattern enum (Entity, ValueObject, Repository, Gateway, Adapter, ...) |
| `fields:` | Yes (may be empty) | Constructor argument shape — `name: Type`. First field is identity for Entity |
| `methods:` | Yes (may be empty) | `methodName(argName: Type): ReturnType`. Use `Type[]` for collections |
| `depends:` | Optional | Sibling or `Module::SiblingClass` references the ICP needs to construct |
| `concretes:` | Optional | Polymorphic implementations (Strategy, Visitor, State variants) |
| `implements:` | Optional | The port/interface this class implements (Adapter / Repository pattern) |
| `invariants:` | Optional | Class-scoped rules — translate to runtime checks |

## Cross-module references

Use `Module::ClassName` for cross-module dependencies. The class must appear in the target module's `EXPORTS` list. The framework's `validate_cross_module_dependencies` validator catches missing exports + cycles BEFORE ICP fan-out.

```
MODULE Forwarding
LAYER Application
EXPORTS [KafkaProducerPort, IngestEventUseCase]
DEPENDS [Ingest::IngestedEvent]              # cross-module dep
CLASSES {
  KafkaProducerPort -> Gateway {
    methods: [publish_event(event: IngestedEvent): None]
    depends: [Ingest::IngestedEvent]          # cross-module
  }
}
```

## Type vocabulary

Squib uses language-neutral type names. Per-language ICPs translate via the **type-fidelity rule** in each language's ICP spec:

| Squib | Python | Java | Go | Rust | JS / TS |
|---|---|---|---|---|---|
| `str` | `str` | `String` | `string` | `String` / `&str` | `string` |
| `int` | `int` | `int` | `int` | `i64` | `number` |
| `float` | `float` | `double` | `float64` | `f64` | `number` |
| `bool` | `bool` | `boolean` | `bool` | `bool` | `boolean` |
| `bytes` | `bytes` | `byte[]` | `[]byte` | `Vec<u8>` / `&[u8]` | `Buffer` |
| `dict[K, V]` | `dict[K, V]` | `Map<K, V>` | `map[K]V` | `HashMap<K, V>` | `Map<K, V>` / `Record<K, V>` |
| `list` / `Type[]` | `list[Type]` | `List<Type>` | `[]Type` | `Vec<Type>` | `Type[]` |
| `set` | `set[Type]` | `Set<Type>` | `map[Type]struct{}` | `HashSet<Type>` | `Set<Type>` |
| `None` | `None` (return) | `void` | (no return) | `()` | `void` |

## Optional ProblemSpec sections

The `ProblemSpec` JSON drives the architect. Beyond `id`, `description`, `acceptance_criteria`, `required_patterns`, `target_language`, four optional sections shape the architect's output further:

| Section | Purpose | Example |
|---|---|---|
| `domain_conventions: ["timeline_includes_self", ...]` | Tags map to canonical INVARIANTs the architect MUST surface verbatim | `timeline_includes_self` → `"a user's timeline must include the user's own posts"` |
| `query_semantics: [{"use_case": "...", "shape": "..."}]` | Declares the query shape per use case | `{"shape": "self_plus_followees"}` |
| `entity_lifecycle: [{"entity": "...", "transitions": [...]}]` | Explicit state machine declarations | Tweet status: `draft → published → deleted` |
| `data_classification: [{"field_ref": "User.password_hash", "sensitivity": "credential"}]` | Sensitivity tags for the SecurityArchitect | `credential` / `pii` / `session_token` |
| `produces_contracts: [{name, transport, fields: [...]}]` | Cross-service contract this service emits | Kafka topic + JSON envelope |
| `consumes_contracts: [{contract_name, role: "consumes"}]` | Cross-service contract this service reads | Resolved from the contract registry |
| `infrastructure_choices: [{category, technology, version_pin}]` | Pin specific SDKs (boto3, spring-kafka, ...) | Drives Tier C ICP routing |

When any of these is present in the user prompt, the architect's spec includes a strict constraint to honor it (constraint #18-#22 in `PrincipalArchitect.md`).

## Validators that run on Squib

Before ICP fan-out, the framework runs five validators against the architect's output:

1. **`ArchitectureSpec.validate()`** — every dep references a known class; cycles forbidden.
2. **`validate_cross_module_dependencies`** — every `Module::Type` is in the target's `EXPORTS`.
3. **`validate_architecture_against_spec`** (F5 conformance) — every declared `domain_conventions` tag appears as INVARIANT; every `data_classification.field_ref` exists.
4. **`validate_http_conventions`** (K4) — HTTP `headers` typed as `dict[str, str]`, body as `bytes`/`str`, etc.
5. **`validate_contract_fidelity`** (case-tolerant) — consumer entities carry producer's contract field names verbatim.

Any validator firing triggers an architect retry with violations appended; second failure aborts the run with an actionable error message.

## See also

- [`architecture.md`](architecture.md) — three-tier model + agent hierarchy
- [`writing_a_problem_spec.md`](writing_a_problem_spec.md) — author's guide with worked examples
