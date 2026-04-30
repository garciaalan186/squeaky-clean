"""P1 Todo Manager (Typescript)."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

P1TS: ProblemSpec = ProblemSpec(
    id="P1TS",
    tier=1,
    slug="todo_manager",
    description=(
        "In-memory todo manager that creates todos with titles, marks them "
        "complete, and lists pending ones. Titles must be non-empty."
    ),
    required_bounded_contexts=["todo"],
    acceptance_criteria=[
        "Given title 'Buy milk', When create_todo is called, Then the result title is 'Buy milk'",
        "Given title 'Task', When create_todo is called, Then the result is_pending is true",
        "Given a fresh todo with title 'Task', after mark_complete is called on it, Then is_pending returns false",
        "Given an empty title, When create_todo is called, Then a ValueError is raised",
        "Given a todo repository containing one pending todo and one completed todo, When list_pending is called, Then the result length is 1",
    ],
    expected_module_count=(1, 3),
    expected_class_count=(5, 12),
    required_patterns=["Entity", "ValueObject", "UseCase", "Repository"],
    target_language=TargetLanguage.TYPESCRIPT,
)
