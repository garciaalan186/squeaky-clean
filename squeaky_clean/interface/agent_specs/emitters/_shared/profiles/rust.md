# Language Profile: Rust (R6.1d delta blocks)

## language_name
Rust

## fence_tag
rust

## input_suffix
, plus an optional Rust `#[cfg(test)]` skeleton for reference

## file_preamble
Start with a single-line `//` comment describing the type. Each file IS a module — declare items directly with `pub`; no module header, no `mod` wrapper.

## abstract_idiom
declare `pub trait <Name> { ... }` with each `methods:` entry as a trait method signature terminated by `;` — NO bodies, NO struct. Methods that "raise" return `Result<T, String>`.

## concrete_idiom
declare `pub struct <Name> { ... }` (snake_case fields from `fields:`) plus `impl <Name> { ... }` with real method bodies. If `implements:` names a sibling trait, ALSO emit `impl <TraitName> for <Name> { ... }` delegating to the inherent methods.

## style_rule
snake_case for methods and fields (§Notation `findById` → `find_by_id`), PascalCase for structs, traits, and enums. Explicit types on every public signature.

## arg_note
(`self`/`&self`/`&mut self` does NOT count)

## import_rule
every sibling import is `use <crate_path>::<ClassName>;` where `<crate_path>` is the EXACT SIBLING_INTERFACES `file=<...>` value translated to Rust path syntax — replace a leading `src.`/`src/` with `crate::` and every remaining `.` or `/` with `::` (e.g. `file=src.domain.auth.user` → `use crate::domain::auth::user::User;`). NEVER invent or shorten the path. Plus `std` only (e.g. `use std::collections::HashMap;`) — no external crates.

## language_rules
0a. **Rendering a "class" in Rust.** A concrete class is `pub struct <Name>` plus an inherent `impl <Name>` block; an abstract participant/port is `pub trait <Name>` with `;`-terminated signatures. Constructors are `pub fn new(...) -> Self` — or `-> Result<Self, String>` when invariants must be validated. When `implements:` names a trait, provide `impl <TraitName> for <Name>`. Entities/Aggregates implement `pub fn equals(&self, other: &Self) -> bool` comparing ONLY the identity field — do NOT `#[derive(PartialEq)]` on them; ValueObjects/DomainEvents instead `#[derive(Debug, Clone, PartialEq)]` and stay immutable (no `&mut self` methods — derive new values by returning new instances).
0b. **Sibling capability fidelity.** Call ONLY the methods and fields the sibling block DECLARES — never invent accessors or operators (`+` on a declared struct type; use its declared methods, e.g. `total = total.add(x)`). If a needed accessor is not declared, use the declared field/method that is.
0c. **§Notation type → Rust type fidelity.** `str` → `String` (parameters may take `&str` where natural), `int` → `i64`, `float` → `f64`, `bool` → `bool`, `None` → `()` (omit the return type), `Type[]` → `Vec<Type>`, `dict` / `dict[K, V]` → `HashMap<K, V>` (`use std::collections::HashMap;`; default `HashMap<String, String>`), `set` → `HashSet<Type>`, `bytes` → `Vec<u8>`. Apply the SAME rendering everywhere the type is referenced — fields, params, returns. A spec `getHistory(): Message[]` is `fn get_history(&self) -> Vec<Message>` — never drop the `Vec`. Match numeric literals to the type (`0` for `i64`, `0.0` for `f64` — mixing them is a compile error).
0d. **Error discipline.** Fallible methods return `Result<T, String>` with `Err("<message>".into())` — NEVER `panic!`, `unwrap()`, `expect()`, `todo!()`, or `unimplemented!()` in domain code. Construction invariants (`"amount must be >= 0"`, `"name must be non-empty"`) are validated in `new(...) -> Result<Self, String>`; method-level invariants are validated inside that method; lifecycle defaults (`"X starts as <value>"`, `"X is initially <value>"`) are set at construction and never rejected.
0e. **Ownership discipline.** Read-only methods take `&self`; mutating methods take `&mut self`; prefer a `.clone()` over fighting the borrow checker within the 80-line budget. Getters return `&T` or a cloned copy — never move a field out of `&self`.
0f. **No `unsafe`.** The declared type name must EXACTLY match the ClassSpec `name`.

## error_rule
Methods that fail return `Result<T, String>` via `Err("<message>".into())` — NEVER `panic!`/`unwrap()`/`expect()` in domain code.

## shadowing_rule
Do not declare a `type` alias, `struct`, or `enum` whose name matches a sibling type.

## fields_rule
Translate every field to a `pub` struct field with the EXACT snake_case spec name, so consumers can read it directly without a getter. Abstract participants (traits) with empty `fields:` declare no struct.

## sibling_fields_rule
When constructing a sibling via `<Sibling>::new(...)` or a struct literal, pass exactly the field values its `fields:` entry declares, in order — and propagate a fallible `new`'s `Result` (with `?` or a `match`); never `unwrap()`. If a sibling's pattern is ValueObject, treat it as immutable: never assign to its fields — build a replacement instance via its constructor with the updated values.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, translate it to `Vec<Type>` and default it to `Vec::new()` inside `new(...)` — construction must work without passing an empty collection.

## floor_expr
`result.max(0)` (or `result.max(0.0)` for `f64`)

## extra_constraints
- **Language recap (Rust).** §Notation types render per the fidelity table (`str`→`String`, `int`→`i64`, `float`→`f64`, `bool`→`bool`, `None`→`()`, `Type[]`→`Vec<Type>`, `dict`→`HashMap<K, V>`); fallible paths return `Result<T, String>` via `Err("...".into())`, never `panic!`/`unwrap()`; no `unsafe`; the declared type name EXACTLY matches the ClassSpec name.

## polymorphism_note
Rust renders the abstract participant as a `trait`; concretes provide working bodies via `impl <Trait> for <Struct>`, and trait objects (`Box<dyn Trait>`) make them interchangeable at runtime.
