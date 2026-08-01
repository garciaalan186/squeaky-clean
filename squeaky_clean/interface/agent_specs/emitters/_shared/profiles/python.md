# Language Profile: Python (R6.1a delta blocks)

## language_name
Python

## fence_tag
python

## input_suffix
, plus an optional pytest test skeleton for reference

## file_preamble
Start with `from __future__ import annotations` as the FIRST import (before abc, before any other import). This enables deferred type annotation evaluation and prevents NameError on self-referential types (e.g., a `Money.add()` method returning `Money`). Follow with a single-line docstring describing the class.

## abstract_idiom
`from abc import ABC, abstractmethod`, declare one class inheriting `ABC`, decorate every method with `@abstractmethod`, method bodies are `...`.

## concrete_idiom
declare one plain class providing real method bodies. It may optionally inherit the abstract participant by its string name if present in the same file context.

## style_rule
Every method annotated (mypy --strict). No `Any`. No `type: ignore`.

## arg_note
(excluding `self`)

## import_rule
every sibling import is `from <dotted_path> import <ClassName>` where `<dotted_path>` is the EXACT value to the right of `file=` in the SIBLING_INTERFACES entry for that class (e.g. `file=src.domain.auth.user` → `from src.domain.auth.user import User`). Use it verbatim. NEVER invent, shorten, or modify the path. NEVER use relative imports (`from .`, `from ..`) or bare-stem imports (`from user import User`). Plus stdlib. No third-party imports.

## language_rules

## error_rule
Raise `ValueError` for invalid inputs rather than silently returning defaults.

## shadowing_rule
Do not declare a module-level type alias whose name matches a sibling class in the same module.

## fields_rule
If the focal ClassSpec has a `fields: [name1: Type1, name2: Type2, ...]` entry, translate every field to an __init__ parameter assigned to self. Use those names verbatim. Do NOT invent additional required state. Abstract participants with empty `fields:` should omit __init__ entirely.

## sibling_fields_rule
The user prompt's SIBLING_INTERFACES block lists every other class's `fields:` and `methods:`. When your implementation instantiates a sibling class, pass exactly the field values its `fields:` entry declares, in order. Do NOT guess constructor shapes.

## collection_default_rule
If a `fields:` entry uses array syntax `Type[]`, translate it to `list[Type]` and default it to `[]` in the `__init__` signature. Tests expect to construct objects without passing empty collections.

## floor_expr
`max(0, result)`

## extra_constraints

## polymorphism_note
Python renders the abstract participant as an ABC with `@abstractmethod`; concretes are plain classes with real bodies.
