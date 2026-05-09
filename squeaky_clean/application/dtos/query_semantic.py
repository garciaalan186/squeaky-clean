"""QuerySemantic DTO: per-use-case query shape declaration."""

from dataclasses import dataclass

_VALID_SHAPES: frozenset[str] = frozenset({
    "self_plus_followees",
    "all_public",
    "paginated",
    "time_windowed",
    "single_by_id",
    "by_author",
})


@dataclass(frozen=True)
class QuerySemantic:
    """Declares the query shape for a named use case."""

    use_case: str
    shape: str

    def __post_init__(self) -> None:
        """Reject unknown shapes; reject empty use_case."""
        if not self.use_case:
            raise ValueError("QuerySemantic.use_case must be non-empty")
        if self.shape not in _VALID_SHAPES:
            raise ValueError(
                f"QuerySemantic.shape {self.shape!r} not in {sorted(_VALID_SHAPES)}"
            )
