"""SecurityConcern DTO: one security concern from the SecurityArchitect."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityConcern:
    """Immutable description of one security concern raised by the SecurityArchitect.

    `category` classifies the concern (e.g. input_validation, boundary).
    `target_class` names the affected class from the ModuleSpec.
    `description` explains the vulnerability.
    `test_scenario` recommends a concrete test in plain English.
    """

    category: str
    target_class: str
    description: str
    test_scenario: str
