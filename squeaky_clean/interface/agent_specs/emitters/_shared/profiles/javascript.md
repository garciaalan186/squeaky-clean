# Language Profile: JavaScript (R6.1a delta blocks)

## language_name
JavaScript

## fence_tag
javascript

## input_suffix
, plus an optional node:test skeleton for reference

## file_preamble
Start with a single-line `//` comment describing the class. Use ES module syntax: `export class <Name> { ... }`. No CommonJS `require`.

## abstract_idiom
declare one plain class with each method body throwing `new Error('abstract method: <name>')`. JavaScript has no true abstract classes — this is the idiomatic substitute.

## concrete_idiom
declare one plain class with real method bodies. Concretes are plain classes; do NOT try to `extends` the abstract participant unless it is a sibling file in `depends:`.

## style_rule
No TypeScript annotations, no `abstract` keyword (not valid in plain JS). Plain JavaScript only.

## arg_note
(excluding `this`)

## import_rule
use the `file=<stem>` value from SIBLING_INTERFACES for flat imports. Write `import { <ClassName> } from './<stem>.js';`. Do NOT guess the file stem from the class name — always use the value shown in `file=<stem>`. Always relative with explicit `.js`.

## language_rules

## error_rule
Throw `new Error(msg)` / `new RangeError(msg)` for invalid inputs rather than silently returning defaults.

## shadowing_rule
Do not declare a top-level `const` or `let` whose name matches a sibling class.

## fields_rule
Translate every field to a constructor parameter assigned via `this.field = param`. Abstract participants with empty `fields:` should omit the constructor entirely.

## sibling_fields_rule
When instantiating a sibling via `new Name(...)`, pass exactly the field values its `fields:` entry declares, in order.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, declare the constructor parameter with a default: `constructor(items = [])`. Assign via `this.items = items;`. Tests expect `new Repository()` with no args.

## floor_expr
`Math.max(0, result)`

## extra_constraints

## polymorphism_note
In JavaScript the abstract participant is a plain class whose methods throw; concretes override them with working bodies.
