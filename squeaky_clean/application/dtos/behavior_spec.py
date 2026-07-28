"""BehaviorSpec: the irreducible behavioral oracle carved out of ProblemSpec.

This is the part of a problem statement that the Squib IR can NOT carry —
the acceptance criteria and the boundary contracts that define *what the code
must do*, and against which the OracleCompiler generates the verifying tests.
Every entry point (requirement, recovered code, hand-authored Squib) must pair
its structure with one of these to be verifiable.
"""

from dataclasses import dataclass, field

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_ref import ContractRef
from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.expected_outcome import ExpectedOutcome


@dataclass(frozen=True)
class BehaviorSpec:
    """The behavioral contract: acceptance oracle + boundary contracts."""

    acceptance_criteria: list[str] = field(default_factory=list)
    produces_contracts: tuple[Contract, ...] = ()
    consumes_contracts: tuple[ContractRef, ...] = ()
    data_classification: tuple[DataClassification, ...] = ()
    expected_outcomes: tuple[ExpectedOutcome, ...] = ()
