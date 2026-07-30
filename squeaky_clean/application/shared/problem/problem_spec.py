"""ProblemSpec DTO: declarative description of one benchmark problem."""

from dataclasses import dataclass

from squeaky_clean.application.generation.techspec.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.generation.validation.contract import Contract
from squeaky_clean.application.generation.validation.contract_ref import ContractRef
from squeaky_clean.application.shared.mcda.data_classification import DataClassification
from squeaky_clean.application.shared.mcda.entity_lifecycle import EntityLifecycle
from squeaky_clean.application.shared.mcda.expected_outcome import ExpectedOutcome
from squeaky_clean.application.shared.mcda.query_semantic import QuerySemantic
from squeaky_clean.application.shared.problem.behavior_spec import BehaviorSpec
from squeaky_clean.application.shared.problem.structural_hints import StructuralHints
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


@dataclass(frozen=True)
class ProblemSpec:
    """Immutable specification of a benchmark problem for the eval harness.

    Decomposed (interface-first) into two cohesive sub-aggregates exposed as
    views: ``behavior`` (the irreducible acceptance oracle + boundary
    contracts) and ``structural_hints`` (the half a Squib can derive — see
    ``derive_structural_hints_from_squib``). The flat fields remain the
    construction surface; Phase A2 migrates storage into ``BehaviorSpec``.
    """

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

    @property
    def behavior(self) -> BehaviorSpec:
        """The behavioral oracle sub-aggregate (what the code must do)."""
        return BehaviorSpec(
            acceptance_criteria=self.acceptance_criteria,
            produces_contracts=self.produces_contracts,
            consumes_contracts=self.consumes_contracts,
            data_classification=self.data_classification,
            expected_outcomes=self.expected_outcomes,
        )

    @property
    def structural_hints(self) -> StructuralHints:
        """The structural sub-aggregate a Squib can derive."""
        return StructuralHints(
            required_bounded_contexts=self.required_bounded_contexts,
            required_patterns=self.required_patterns,
            expected_module_count=self.expected_module_count,
            expected_class_count=self.expected_class_count,
        )
