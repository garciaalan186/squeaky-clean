"""TestSkeleton DTO: a pytest test file stub for one target class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TestSkeleton:
    """Immutable pytest test file stub emitted by the TestArchitect.

    Fields follow the Phase 3 TestArchitect output contract: `class_name`
    names the target class under test, `file_path` is the intended test
    file location (e.g. ``tests/test_calculator.py``), and `code` holds a
    complete pytest source file with imports plus one test function per
    public method on the target class. Each test body must be a
    ``pytest.fail("not implemented")`` placeholder — no production logic.
    """

    class_name: str
    file_path: str
    code: str
