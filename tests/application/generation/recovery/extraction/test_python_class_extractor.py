"""Tests for PythonClassExtractor: one parsed module -> ClassRecords."""

import ast

from squeaky_clean.application.generation.recovery.extraction.python_class_extractor import (
    PythonClassExtractor,
)


def test_only_top_level_classes_are_catalogued() -> None:
    module = ast.parse(
        "class A:\n"
        "    class Inner: ...\n"
        "class B: ...\n",
    )
    records = PythonClassExtractor().extract(module, "proj.mod")
    assert tuple(r.fqn for r in records) == ("proj.mod.A", "proj.mod.B")


def test_file_level_imports_attach_to_every_class() -> None:
    module = ast.parse(
        "import os\n"
        "from proj.base import Base\n"
        "class A: ...\n"
        "class B: ...\n",
    )
    records = PythonClassExtractor().extract(module, "proj.mod")
    assert records[0].imports == ("os", "proj.base.Base")
    assert records[1].imports == ("os", "proj.base.Base")


def test_relative_from_import_without_module_is_skipped() -> None:
    module = ast.parse("from . import helper\nclass A: ...\n")
    records = PythonClassExtractor().extract(module, "proj.mod")
    assert records[0].imports == ()


def test_module_with_no_classes_yields_empty_tuple() -> None:
    module = ast.parse("x = 1\n")
    assert PythonClassExtractor().extract(module, "proj.mod") == ()
