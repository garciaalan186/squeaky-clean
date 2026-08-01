# Language Profile: Go (R6.1d delta blocks)

## language_name
Go

## fence_tag
go

## input_suffix
, plus an optional Go testing skeleton for reference

## file_preamble
Start with a single-line `//` comment describing the type. **The first non-comment line MUST be `package main`** — every generated Go file lives in the single flat `package main`; never invent another package name.

## abstract_idiom
declare `type <Name> interface { ... }` with each `methods:` entry as an interface method signature — no bodies, no struct. Methods that "raise" declare `error` as the last return value.

## concrete_idiom
declare `type <Name> struct { ... }` (exported PascalCase fields from `fields:`) plus receiver methods on `*<Name>` with real bodies. It satisfies the abstract participant implicitly — Go uses structural typing; there is NO `implements` keyword to write.

## style_rule
Exported PascalCase names for the declared type, its fields, and its methods (§Notation `find_by_id`/`findById` → `FindByID`); unexported camelCase only for internal helpers. Use tabs (gofmt style).

## arg_note
(the receiver does NOT count)

## import_rule
sibling classes live in the same `package main`, so they need NO import — reference sibling types directly and NEVER emit an import derived from a sibling's `file=` value. Import ONLY the stdlib packages actually used (e.g. `"fmt"`), with `import ( ... )` block syntax when importing more than one. No third-party imports. Every imported package MUST be used — an unused import is a Go compile error.

## language_rules
0a. **Rendering a "class" in Go.** A concrete class is `type <Name> struct { ... }` with receiver methods (`func (x *<Name>) Method(...)`); an abstract participant/port is `type <Name> interface { ... }` with signatures only, satisfied implicitly — never write an `implements` clause. When the ClassSpec declares fields or invariants, provide a `New<Name>(...)` constructor — returning `(<Name>, error)` if construction validates invariants, plain `<Name>` otherwise. Where the pattern calls for identity-based equality (Entity/Aggregate), implement `Equals(other *<Name>) bool` comparing ONLY the identity field — never whole-struct comparison; where it calls for value semantics (ValueObject/DomainEvent), keep the type immutable by convention (no mutating methods; derive new values by constructing new instances).
0b. **Sibling capability fidelity.** Call ONLY the methods and fields the sibling block DECLARES — never invent getters or operators (`+` on a declared struct type; use its declared methods, e.g. `total = total.Add(x)`). If a needed accessor is not declared, use the declared field/method that is.
0c. **§Notation type → Go type fidelity.** `str` → `string`, `int` → `int`, `float` → `float64` (NEVER `float32`), `bool` → `bool`, `None` → no return value, `Type[]` → `[]Type`, `dict` / `dict[K, V]` → `map[K]V` (default `map[string]string`), `set` → `map[Type]struct{}`, `bytes` → `[]byte`. Apply the SAME rendering everywhere the type is referenced — fields, params, returns. A spec `getHistory(): Message[]` is `GetHistory() []Message` — never drop the slice, never substitute another collection.
0d. **Error discipline.** Fallible methods return `error` as the LAST return value, built with `fmt.Errorf("<message>")` — NEVER `panic` in domain code. Construction invariants (`"amount must be >= 0"`, `"name must be non-empty"`) are validated in `New<Name>(...)`, returning the zero value plus the error; method-level invariants are validated inside that method and return an error; lifecycle defaults (`"X starts as <value>"`, `"X is initially <value>"`) are set at construction and never rejected.
0e. **Collection zero values.** `Type[]` fields become `[]Type`; Go's nil slice is a valid empty collection, so zero-value construction is already correct — no special empty-slice initialization is required.
0f. **No `init()` functions; no goroutines unless the spec demands concurrency.** The declared type name must EXACTLY match the ClassSpec `name`.

## error_rule
Methods that fail return `fmt.Errorf("<message>")` as their `error` value — NEVER `panic` in domain code.

## shadowing_rule
Do not declare a top-level type, alias, or variable whose name matches a sibling type.

## fields_rule
Translate every field to a struct field with the EXACT spec name, exported (PascalCase the spec name; `id` → `ID`). Abstract participants with empty `fields:` declare no struct.

## sibling_fields_rule
When constructing a sibling via `New<Sibling>(...)` or a struct literal, pass exactly the field values its `fields:` entry declares, in order — and handle the `error` if its constructor returns one. If a sibling's pattern is ValueObject, treat it as immutable: never assign to its fields — build a replacement instance via its constructor with the updated values.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, translate it to `[]Type`. A nil slice is a valid empty slice — construction without the collection argument must work (zero value, or `New<Name>()` defaulting the slice).

## floor_expr
`max(0, result)` (built-in `max`, Go 1.21+)

## extra_constraints
- **Language recap (Go).** §Notation types render per the fidelity table (`str`→`string`, `int`→`int`, `float`→`float64`, `bool`→`bool`, `None`→no return, `Type[]`→`[]Type`, `dict`→`map[K]V`); fallible methods return `error` via `fmt.Errorf(...)`, never `panic`; the declared type name EXACTLY matches the ClassSpec name; unused imports and variables are compile errors — import only what is used.

## polymorphism_note
Go renders the abstract participant as an `interface`; concrete structs satisfy it implicitly through matching method sets (structural typing — no `implements` keyword).
