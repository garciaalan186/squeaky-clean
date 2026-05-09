"""ImplementedClass DTO: one ICP output — production code plus optional test."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ImplementedClass:
    """Immutable record of what an ICP actually emitted for one class.

    ``class_name`` is the PascalCase identifier. ``file_path`` is the
    intended production file location. ``code`` is the extracted Python
    source (fence already stripped). ``test_code`` holds the test file
    body if the ICP also emitted one; ICPs that only produce production
    code leave this as ``None``. ``cost_usd`` and ``duration_ms`` come
    from the LLM response metadata for the single ICP call that produced
    this class — OrchestrateModule sums these across all classes in the
    module to populate ModuleImplementation.
    """

    class_name: str
    file_path: str
    code: str
    test_code: str | None
    cost_usd: float
    duration_ms: int
    input_tokens: int
    output_tokens: int
    retries: int = 0
