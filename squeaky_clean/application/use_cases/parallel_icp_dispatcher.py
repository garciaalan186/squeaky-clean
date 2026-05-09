"""ParallelICPDispatcher: run ImplementClass across many assignments via threads."""

from concurrent.futures import ThreadPoolExecutor

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.implement_class import ImplementClass

_MAX_WORKERS: int = 4


class ParallelICPDispatcher:
    """Runs ImplementClass over a list of assignments using a thread pool."""

    def __init__(self, implement_class: ImplementClass) -> None:
        self._implement: ImplementClass = implement_class

    def dispatch(
        self,
        assignments: tuple[ClassAssignment, ...],
    ) -> tuple[ImplementedClass, ...]:
        """Run every assignment in parallel; return results in input order."""
        if not assignments:
            return ()
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            results = list(pool.map(self._implement.execute, assignments))
        return tuple(results)
