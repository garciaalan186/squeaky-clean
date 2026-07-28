"""P9 Drawing Canvas: exercises Composite (shape tree) + Visitor (area traversal)."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P9: ProblemSpec = ProblemSpec(
    id="P9",
    tier=9,
    slug="drawing_canvas",
    description=(
        "A drawing composed of shapes and groups. A rectangle has width and "
        "height; a group holds any number of shapes or nested groups, treated "
        "uniformly as a composite. An area visitor traverses the tree and "
        "computes the total area across all leaf shapes."
    ),
    required_bounded_contexts=["drawing"],
    acceptance_criteria=[
        "Given a group containing a rectangle 2 by 3 and a rectangle 4 by 5, When total area is computed, Then it is 26",
        "Given an empty group, When total area is computed, Then it is 0",
        "Given a group containing a rectangle 2 by 3, When another rectangle is added, Then the group child count is 2",
        "Given a group containing a nested group with a rectangle 3 by 3, When total area is computed, Then it is 9",
        "Given a single rectangle 5 by 4 visited by the area visitor, When its area is computed, Then it is 20",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 14),
    required_patterns=["Composite", "Visitor", "ValueObject", "SimpleClass"],
    target_language=TargetLanguage.PYTHON,
)
