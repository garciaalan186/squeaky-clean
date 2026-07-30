"""ClassRecord DTO: deterministic AST facts about one existing class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassRecord:
    """Reproducible AST facts extracted from one class in a brownfield repo.

    `fqn` is the dotted path derived from the source file's location plus
    the class name (e.g. ``myproj.domain.user.User``). `bases` are the
    base-class names as written. `methods` are public method signatures
    rendered ``name(arg, arg)`` (dunder/underscore-prefixed excluded).
    `fields` are ``name: Type`` strings from annotated class-level
    attributes and ``self.<name>`` assignments. `imports` are the dotted
    targets imported by the class's source file. `decorators` are the
    decorator names applied to the class. No LLM produces any of this;
    the extraction is byte-for-byte reproducible across runs.
    """

    fqn: str
    bases: tuple[str, ...]
    methods: tuple[str, ...]
    fields: tuple[str, ...]
    imports: tuple[str, ...]
    decorators: tuple[str, ...]
