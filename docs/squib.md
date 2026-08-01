# Squib — Grammar Reference

Squib is the compact text format the RequirementCompiler emits and emitters consume. It is the framework's instruction set architecture.

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
| `INVARIANTS [...]` | Yes (may be empty) | Module-level invariants surfaced to all emitters in this module |

## Class definitions

| Field | Required | Notes |
|---|---|---|
| `<ClassName> -> <PatternName>` | Yes | PatternName from the 34-pattern enum (Entity, ValueObject, Repository, Gateway, Adapter, ...) |
| `fields:` | Yes (may be empty) | Constructor argument shape — `name: Type`. First field is identity for Entity |
| `methods:` | Yes (may be empty) | `methodName(argName: Type): ReturnType`. Use `Type[]` for collections |
| `depends:` | Optional | Sibling or `Module::SiblingClass` references the emitter needs to construct |
| `concretes:` | Optional | Polymorphic implementations (Strategy, Visitor, State variants). Derived from same-pattern `depends:` edges when omitted — see [Polymorphic roles](#polymorphic-roles) |
| `implements:` | Optional | The port/interface or abstract participant this class implements (Adapter / Repository; also stamped on polymorphic concretes). Declaring it marks the named class an abstraction — see [Polymorphic roles](#polymorphic-roles) |
| `invariants:` | Optional | Class-scoped rules — translate to runtime checks |

## Polymorphic roles

Seven pattern families split their participants into one abstract base plus polymorphic concretes: **Strategy, State, Visitor, Observer, Command, TemplateMethod, ChainOfResponsibility**. Emitters decide whether to emit an interface or a concrete class from `concretes:` / `implements:`, and there are two equivalent ways to express that split.

That decision is named once, on the entity: `ClassSpec.role()` returns a `ClassRole` of `ABSTRACT` when the class declares `concretes:` (emitters render it as an interface), `CONCRETE` when it declares an `implements:` target, and `PLAIN` otherwise.

Canonical — the abstract declares its `concretes:`, each concrete declares `implements:`:

```
CLASSES {
  PaymentProcessor -> Strategy {
    methods:   [execute(payment: Payment): Result]
    concretes: [CreditCardProcessor, PayPalProcessor]
  }
  CreditCardProcessor -> Strategy {
    methods:    [execute(payment: Payment): Result]
    implements: PaymentProcessor
  }
  PayPalProcessor -> Strategy {
    methods:    [execute(payment: Payment): Result]
    implements: PaymentProcessor
  }
}
```

Peer — each concrete simply points at the abstract with `depends:`, and no class declares `concretes:`:

```
CLASSES {
  PaymentProcessor -> Strategy {
    methods: [execute(payment: Payment): Result]
  }
  CreditCardProcessor -> Strategy {
    methods: [execute(payment: Payment): Result]
    depends: [PaymentProcessor]
  }
  PayPalProcessor -> Strategy {
    methods: [execute(payment: Payment): Result]
    depends: [PaymentProcessor]
  }
}
```

Before emitter fan-out, `PolymorphicRoleNormalizer` reads a `depends:` edge between two classes in the same module carrying the **same** polymorphic pattern name as concrete → abstract: the named classes are appended to the abstract's `concretes:`, and `implements:` is stamped on each concrete. Anything already declared is preserved and merged without duplicates, so both shapes above generate identical code. The pass is a pure function — no LLM call, no added cost.

Both shapes carry fixture coverage: `eval/squib_fixtures/` holds a `*_depends_shape.squib` fixture for each of the seven families alongside the canonical ones, so the peer shape is compile-checked by `--micro-evals` too.

`implements:` is read pattern-agnostically in the same pass: any declared `implements: X` marks X an abstract participant and stamps the declaring class onto X's `concretes:`, whatever pattern X itself carries. An Adapter's port declared as `SimpleClass` therefore still renders as an interface rather than as a second concrete class.

Two kinds of edge are deliberately left alone, because they are ordinary collaboration rather than a role split:

- edges between classes of **different** patterns — an `Entity` that `depends:` on a `Strategy` stays a collaborator;
- edges between classes whose pattern is **not** one of the seven — `Entity` → `Entity`, `UseCase` → `Repository`, and so on.

## Cross-module references

Use `Module::ClassName` for cross-module dependencies. The class must appear in the target module's `EXPORTS` list. The framework's `validate_cross_module_dependencies` validator catches missing exports + cycles BEFORE emitter fan-out.

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

Squib uses language-neutral type names. Per-language emitters translate via the **type-fidelity rule** in each language's emitter spec:

| Squib | Python | Java | JS / TS |
|---|---|---|---|
| `str` | `str` | `String` | `string` |
| `int` | `int` | `int` | `number` |
| `float` | `float` | `double` | `number` |
| `bool` | `bool` | `boolean` | `boolean` |
| `bytes` | `bytes` | `byte[]` | `Buffer` |
| `dict[K, V]` | `dict[K, V]` | `Map<K, V>` | `Map<K, V>` / `Record<K, V>` |
| `list` / `Type[]` | `list[Type]` | `List<Type>` | `Type[]` |
| `set` | `set[Type]` | `Set<Type>` | `Set<Type>` |
| `None` | `None` (return) | `void` | `void` |

## Optional ProblemSpec sections

The `ProblemSpec` JSON drives the architect. Beyond `id`, `description`, `acceptance_criteria`, `required_patterns`, `target_language`, four optional sections shape the architect's output further:

| Section | Purpose | Example |
|---|---|---|
| `domain_conventions: ["timeline_includes_self", ...]` | Tags map to canonical INVARIANTs the architect MUST surface verbatim | `timeline_includes_self` → `"a user's timeline must include the user's own posts"` |
| `query_semantics: [{"use_case": "...", "shape": "..."}]` | Declares the query shape per use case | `{"shape": "self_plus_followees"}` |
| `entity_lifecycle: [{"entity": "...", "transitions": [...]}]` | Explicit state machine declarations | Tweet status: `draft → published → deleted` |
| `data_classification: [{"field_ref": "User.password_hash", "sensitivity": "credential"}]` | Sensitivity tags for the ThreatAnalyzer | `credential` / `pii` / `session_token` |
| `produces_contracts: [{name, transport, fields: [...]}]` | Cross-service contract this service emits | Kafka topic + JSON envelope |
| `consumes_contracts: [{contract_name, role: "consumes"}]` | Cross-service contract this service reads | Resolved from the contract registry |
| `infrastructure_choices: [{category, technology, version_pin}]` | Pin specific SDKs (boto3, spring-kafka, ...) | Drives Tier C emitter routing |

When any of these is present in the user prompt, the architect's spec includes a strict constraint to honor it (constraint #18-#22 in `RequirementCompiler.md`).

## Validators that run on Squib

Before emitter fan-out, the framework runs five validators against the architect's output:

1. **`ArchitectureSpec.validate()`** — every dep references a known class; cycles forbidden.
2. **`validate_cross_module_dependencies`** — every `Module::Type` is in the target's `EXPORTS`.
3. **`validate_architecture_against_spec`** (F5 conformance) — every declared `domain_conventions` tag appears as INVARIANT; every `data_classification.field_ref` exists.
4. **`validate_http_conventions`** (K4) — HTTP `headers` typed as `dict[str, str]`, body as `bytes`/`str`, etc.
5. **`validate_contract_fidelity`** (case-tolerant) — consumer DTOs carry the producer's contract field names verbatim.

Any validator firing triggers an architect retry with violations appended; second failure aborts the run with an actionable error message.

The §Notation invariants themselves are stated once, on the entities and the domain rules that own them, rather than restated by each validator. `ClassSpec` and `ModuleSpec` expose `unknown_dep_violations()` and `field_syntax_violations()`; the strict per-edge `Module::Type` checks live in `squeaky_clean/domain/rules/cross_module_dependency_rules.py` and surface as `ArchitectureSpec.cross_module_dep_violations()`, over which `validate_cross_module_dependencies` is a thin seam.

## Shape novelty

Every run also classifies the shapes the architect actually emitted. A **shape** is a class's pattern name plus which of `fields`, `methods`, `depends`, `concretes`, `implements` and `invariants` it declares. The `.squib` fixtures in `eval/squib_fixtures/` define the known set: every shape appearing in that corpus is a tested construction.

`EvalMetrics.notation.notation_novelty` counts the emitted constructions whose shape the corpus has never seen, and is reported in `eval_report.json` under the `notation` group. It is observational — it never gates and is not part of the regression gate. Each run writes `notation_novelty.json` beside the emitted notation:

```json
{"count": 2, "novel": ["Entity:110001", "Repository:011000"]}
```

The list is sorted, and the six flag bits are `fields`, `methods`, `depends`, `concretes`, `implements`, `invariants` in that order. When the count is non-zero the raw notation is also copied into `<results-root>/notation-triage/`, named after the run and problem-set directories, so a new architect shape is adopted into the fixture corpus deliberately instead of being met first in production as a downstream contract break. The harvest is best-effort: if it cannot be written the run is unaffected and the sidecar still records the count, and the failure is recorded as a `notation_triage_write_failed` event in the structured JSON run log rather than passing unnoticed. Notation that fails to parse reports zero and writes no sidecar.

## See also

- [`architecture.md`](architecture.md) — three-tier model + agent hierarchy
- [`writing_a_problem_spec.md`](writing_a_problem_spec.md) — author's guide with worked examples
