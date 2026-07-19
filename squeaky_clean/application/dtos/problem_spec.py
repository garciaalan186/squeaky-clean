"""ProblemSpec DTO: declarative description of one benchmark problem."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_ref import ContractRef
from squeaky_clean.application.dtos.data_classification import DataClassification
from squeaky_clean.application.dtos.entity_lifecycle import EntityLifecycle
from squeaky_clean.application.dtos.expected_outcome import ExpectedOutcome
from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.query_semantic import QuerySemantic
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


@dataclass(frozen=True)
class ProblemSpec:
    """Immutable specification of a benchmark problem for the eval harness."""

    id: str
    tier: int
    slug: str
    description: str
    required_bounded_contexts: list[str]
    acceptance_criteria: list[str]
    expected_module_count: tuple[int, int]
    expected_class_count: tuple[int, int]
    required_patterns: list[str]
    target_language: TargetLanguage
    domain_conventions: tuple[str, ...] = ()
    query_semantics: tuple[QuerySemantic, ...] = ()
    entity_lifecycle: tuple[EntityLifecycle, ...] = ()
    data_classification: tuple[DataClassification, ...] = ()
    infrastructure_choices: tuple[InfrastructureChoice, ...] = ()
    mcda_weights: dict[str, float] | None = None
    produces_contracts: tuple[Contract, ...] = ()
    consumes_contracts: tuple[ContractRef, ...] = ()
    expected_outcomes: tuple[ExpectedOutcome, ...] = ()
