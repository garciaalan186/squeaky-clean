"""P0TS Calculator: TypeScript proof-of-concept benchmark."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P0TS: ProblemSpec = ProblemSpec(
    id="P0TS",
    tier=0,
    slug="calculator",
    description="Calculator with four basic arithmetic operations",
    required_bounded_contexts=["calculator"],
    acceptance_criteria=[
        "Given operands 2 and 3, When add is called, Then result is 5",
        "Given operands 5 and 2, When subtract is called, Then result is 3",
        "Given operands 4 and 3, When multiply is called, Then result is 12",
        "Given operands 10 and 2, When divide is called, Then result is 5",
        "Given operands 1 and 0, When divide is called, Then an error is raised",
    ],
    expected_module_count=(1, 1),
    expected_class_count=(3, 6),
    required_patterns=["SimpleClass", "ValueObject"],
    target_language=TargetLanguage.TYPESCRIPT,
)
