"""ObligationTestFileLocator: maps gapped obligations to their test files."""

import re
from pathlib import Path

from squeaky_clean.application.generation.repair.obligations.obligation_repair_request import (
    ObligationRepairRequest,
)
from squeaky_clean.application.generation.repair.obligations.obligation_test_path_namer import (
    ObligationTestPathNamer,
)
from squeaky_clean.application.generation.testgen.test_obligation import TestObligation

_TEST_FILE = re.compile(r"(^test_.*\.py$|\.test\.(ts|js)$|Test\.java$)")


class ObligationTestFileLocator:
    """Groups obligations by the test file that must discharge them."""

    def __init__(self) -> None:
        self._namer: ObligationTestPathNamer = ObligationTestPathNamer()

    def group(
        self, gaps: tuple[TestObligation, ...], request: ObligationRepairRequest,
    ) -> dict[str, list[TestObligation]]:
        """Map relative test-file path -> obligations it must discharge."""
        by_file: dict[str, list[TestObligation]] = {}
        for gap in gaps:
            # Constructor-invariant duties go to a fresh dedicated file: the
            # repairer reliably CREATES a clean invariants test, whereas
            # asking it to graft an assertion into an existing storage-test
            # file is unreliable.
            rel = (self._namer.invariants_path(gap.target_class, request.toolkit)
                   if gap.method == "<init>"
                   else self._test_file_for(gap.target_class, request))
            if rel is not None:
                by_file.setdefault(rel, []).append(gap)
        return by_file

    def _test_file_for(
        self, class_name: str, request: ObligationRepairRequest,
    ) -> str | None:
        """The class's own test file — an existing one, else a new path.

        Prefers a test file whose stem is the class name; falls back to any
        test that references it; when none exists, returns a canonical new
        path so the repairer CREATES the missing test.
        """
        forms = self._namer.forms(class_name)
        named: str | None = None
        mentions: str | None = None
        for p in sorted(request.output_dir.rglob("*")):
            if (not p.is_file() or not _TEST_FILE.search(p.name)
                    or "node_modules" in p.parts or "target" in p.parts):
                continue
            stem = p.name.split(".")[0].replace("Test", "")
            rel = str(p.relative_to(request.output_dir))
            if stem in forms and named is None:
                named = rel
            elif mentions is None and re.search(
                    rf"\b{re.escape(class_name)}\b", self._read(p)):
                mentions = rel
        return named or mentions or self._namer.canonical(
            class_name, request.toolkit,
        )

    @staticmethod
    def _read(path: Path) -> str:
        try:
            return path.read_text()
        except OSError:
            return ""
