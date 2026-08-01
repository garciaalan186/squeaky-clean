# Language Profile: TypeScript (R6.1a delta blocks)

## language_name
TypeScript

## fence_tag
typescript

## input_suffix
, plus an optional node:test skeleton for reference

## file_preamble
Start with a single-line `//` comment describing the class. Use ES module syntax: `export abstract class <Name>` or `export class <Name>`.

## abstract_idiom
declare an `export abstract class` with each method marked `abstract` with full type signatures but no body.

## concrete_idiom
declare `export class <Name> extends <AbstractName>` with real method bodies and full type annotations.

## style_rule
**Full type annotations.** Every parameter, return type, and field must have explicit TypeScript types.

## arg_note
(excluding `this`)

## import_rule
use the `file=<stem>` value from SIBLING_INTERFACES or TARGET_FILE. Write `import { <ClassName> } from './<stem>.js';` (`.js` extension required by nodenext). NEVER guess the file name from the class name — always use the value shown in `file=<stem>`.

## language_rules

## error_rule
Throw `new Error(msg)` / `new RangeError(msg)` for invalid inputs rather than silently returning defaults.

## shadowing_rule
Do not declare a top-level `const` or `let` whose name matches a sibling class.

## fields_rule
Translate every field to a typed constructor parameter assigned via `this.field = param`. Abstract participants with empty `fields:` should omit the constructor entirely.

## sibling_fields_rule
When instantiating a sibling via `new Name(...)`, pass exactly the field values its `fields:` entry declares, in order.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, declare `constructor(items: Type[] = [])`. Tests expect `new Repository()` with no args.

## floor_expr
`Math.max(0, result)`

## extra_constraints

## polymorphism_note
TypeScript supports `abstract class` natively; concretes `extends` the base with implemented bodies.
