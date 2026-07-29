"""Violation DTO: one architectural rule violation record."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    """Immutable record of a single rule violation in generated code.

    `rule_name` is the class name of the rule that fired (e.g.
    ``GranularityRule``). `file_path` is a string path (relative or
    absolute is fine — the report just echoes it back). `message`
    is a one-line human-readable description of the violation.
    """

    rule_name: str
    file_path: str
    message: str
