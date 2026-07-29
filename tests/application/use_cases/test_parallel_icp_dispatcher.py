"""Tests for ParallelICPDispatcher error isolation (R0.6)."""

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.parallel_icp_dispatcher import (
    ParallelICPDispatcher,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _assignment(name: str) -> ClassAssignment:
    cls = ClassSpec(
        name=name, pattern="SimpleClass", implements=None,
        methods=(), depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="M", layer=LayerType.DOMAIN, exports=(name,), depends=(),
        classes=(cls,), invariants=(),
    )
    return ClassAssignment(
        class_spec=cls, module=module, toolkit=_TOOLKIT,
        emitter_spec_name="python/ddd_clean/SimpleClassEmitter",
        file_path=f"src/{name.lower()}.py",
        test_file_path=f"tests/test_{name.lower()}.py",
    )


def _impl(name: str) -> ImplementedClass:
    return ImplementedClass(
        class_name=name, file_path=f"src/{name.lower()}.py",
        code="x = 1", test_code=None, cost_usd=0.0, duration_ms=1,
        input_tokens=1, output_tokens=1, retries=0,
    )


class _FlakyImplement:
    """Fails on one named class, succeeds on the rest."""

    def __init__(self, fail_on: str) -> None:
        self._fail_on = fail_on

    def execute(self, assignment: ClassAssignment) -> ImplementedClass:
        if assignment.class_spec.name == self._fail_on:
            raise RuntimeError("emitter parse failure")
        return _impl(assignment.class_spec.name)


def test_one_failure_does_not_kill_the_batch() -> None:
    assignments = tuple(_assignment(n) for n in ("A", "B", "C", "D"))
    dispatcher = ParallelICPDispatcher(_FlakyImplement(fail_on="C"))  # type: ignore[arg-type]
    results = dispatcher.dispatch(assignments)
    names = {r.class_name for r in results}
    assert names == {"A", "B", "D"}  # 3 survive, C's failure isolated


def test_empty_assignments_returns_empty() -> None:
    dispatcher = ParallelICPDispatcher(_FlakyImplement(fail_on=""))  # type: ignore[arg-type]
    assert dispatcher.dispatch(()) == ()


def test_all_success_preserves_order() -> None:
    assignments = tuple(_assignment(n) for n in ("A", "B", "C"))
    dispatcher = ParallelICPDispatcher(_FlakyImplement(fail_on="none"))  # type: ignore[arg-type]
    results = dispatcher.dispatch(assignments)
    assert [r.class_name for r in results] == ["A", "B", "C"]


class _BarrierImplement:
    """Blocks each call on a barrier so all run concurrently (peak gauge test)."""

    def __init__(self, parties: int) -> None:
        import threading
        self._barrier = threading.Barrier(parties, timeout=5)

    def execute(self, assignment: ClassAssignment) -> ImplementedClass:
        self._barrier.wait()
        return _impl(assignment.class_spec.name)


def test_peak_parallelism_is_measured() -> None:
    assignments = tuple(_assignment(n) for n in ("A", "B", "C", "D"))
    dispatcher = ParallelICPDispatcher(
        _BarrierImplement(4), max_workers=4,  # type: ignore[arg-type]
    )
    dispatcher.dispatch(assignments)
    # All four are forced to rendezvous at the barrier → peak is exactly 4.
    assert dispatcher.peak_parallelism == 4


def test_peak_parallelism_never_exceeds_workers() -> None:
    assignments = tuple(_assignment(n) for n in ("A", "B", "C"))
    dispatcher = ParallelICPDispatcher(
        _FlakyImplement(fail_on="none"), max_workers=2,  # type: ignore[arg-type]
    )
    dispatcher.dispatch(assignments)
    assert 1 <= dispatcher.peak_parallelism <= 2
