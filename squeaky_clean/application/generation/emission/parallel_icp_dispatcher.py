"""ParallelICPDispatcher: run ImplementClass across many assignments via threads."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.application.generation.emission.implement_class import ImplementClass
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass

_LOG = logging.getLogger(__name__)
_MAX_WORKERS: int = 4


class ParallelICPDispatcher:
    """Runs ImplementClass over a list of assignments using a thread pool.

    ``peak_parallelism`` records the highest number of ICPs observed running
    concurrently during the last ``dispatch`` — the measured counterpart to the
    configured ``max_workers`` cap (EvalMetrics.peak_parallelism).
    """

    def __init__(
        self, implement_class: ImplementClass, max_workers: int = _MAX_WORKERS,
    ) -> None:
        self._implement: ImplementClass = implement_class
        self._max_workers: int = max_workers
        self.peak_parallelism: int = 0
        self._active: int = 0
        self._gauge_lock: Lock = Lock()

    def dispatch(
        self,
        assignments: tuple[ClassAssignment, ...],
    ) -> tuple[ImplementedClass, ...]:
        """Run every assignment in parallel; return successes in input order.

        A failing assignment is logged and skipped so its siblings' completed
        work survives (partial results) — unlike ``pool.map``, whose first
        raised exception cancels the batch and discards everything.
        """
        if not assignments:
            return ()
        self.peak_parallelism = 0
        results: dict[int, ImplementedClass] = {}
        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            futures = {
                pool.submit(self._run, assignment): index
                for index, assignment in enumerate(assignments)
            }
            for future in as_completed(futures):
                index = futures[future]
                try:
                    results[index] = future.result()
                except Exception as exc:  # noqa: BLE001
                    _LOG.warning(
                        "ICP failed for %s: %s",
                        assignments[index].class_spec.name, exc,
                    )
        return tuple(results[i] for i in sorted(results))

    def _run(self, assignment: ClassAssignment) -> ImplementedClass:
        """Execute one ICP, tracking peak concurrency around the call."""
        with self._gauge_lock:
            self._active += 1
            self.peak_parallelism = max(self.peak_parallelism, self._active)
        try:
            return self._implement.execute(assignment)
        finally:
            with self._gauge_lock:
                self._active -= 1
