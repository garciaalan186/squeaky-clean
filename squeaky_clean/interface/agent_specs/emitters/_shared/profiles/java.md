# Language Profile: Java (R6.1a delta blocks)

## language_name
Java

## fence_tag
java

## input_suffix


## file_preamble
Start with a single-line `//` comment describing the type. **The very first non-comment line MUST be `package com.example;`** — every Java file in this project lives in the `com.example` package; default package is forbidden.

## abstract_idiom
declare one `public interface <Name>` with method signatures (no bodies). Java has real interfaces.

## concrete_idiom
declare one `public class <Name> implements <InterfaceName>` with real method bodies and `@Override` on each interface method.

## style_rule
Use camelCase for methods, PascalCase for class and interface names.

## arg_note
(constructors do NOT count)

## import_rule
**Standard library imports.** If any field, parameter, or return type uses `java.util` classes (List, ArrayList, Map, HashMap, Set, HashSet, Collections), generate the necessary import statements (e.g. `import java.util.List;`, `import java.util.ArrayList;`). Also import `java.util.Objects` if using `Objects.hash()` or `Objects.equals()`. **Sibling classes ARE in `com.example` so they need NO explicit import.**

## language_rules
0c. **Sibling capability fidelity.** Call ONLY the methods and fields the sibling block DECLARES — never invent getters (`getUsername()` when the sibling declares `getName()`) or operators (`+` on a declared class type; use its declared methods, e.g. `total = total.add(x)`). If a needed accessor is not declared, use the declared field/method that is.
0. **§Notation type → Java type fidelity.** `str` → `String`, `int` → `int`, `float` → `double` (NEVER Java `float` — mixing `float` fields with `double` arithmetic is a lossy-conversion compile error), `bool` → `boolean`, `None` → `void`; `Type[]` → `List<Type>` (import `java.util.List`), `dict` → `Map<K, V>`. Apply the SAME rendering everywhere the type is referenced — fields, params, returns.

## error_rule
Throw `new IllegalArgumentException(msg)` for invalid inputs.

## shadowing_rule
Do not declare a nested or local type whose name matches a sibling class.

## fields_rule
Translate every field to a constructor parameter assigned via `this.field = param`. Abstract participants with empty `fields:` should have no constructor.

## sibling_fields_rule
When instantiating a sibling, pass exactly the field values its `fields:` entry declares.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, provide TWO constructors: one accepting `List<Type>` and one no-arg constructor that defaults to `new ArrayList<>()`. Tests may call `new Repository()` with no args. Use `import java.util.ArrayList;`.

## floor_expr
`Math.max(0, result)`

## extra_constraints
11. **Class name must EXACTLY match the ClassSpec name.** The generated declaration must be `public class <EXACT_NAME>` or `public interface <EXACT_NAME>` where `<EXACT_NAME>` is the `name` field from the ClassSpec. Do NOT rename, abbreviate, or modify the class name in any way.

## polymorphism_note
Java renders the abstract participant as an `interface`; concretes use `implements` with real bodies.
