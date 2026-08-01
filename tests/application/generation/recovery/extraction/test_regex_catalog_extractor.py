"""Tests for RegexCatalogExtractor: the shared walk/read/resolve scaffold."""

from pathlib import Path

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.extraction.regex_catalog_extractor import (
    RegexCatalogExtractor,
)


class _FakeExtractor(RegexCatalogExtractor):
    """Records one class per file whose import targets the sibling file."""

    _GLOB = "*.fake"

    def _records(self, source: str, prefix: str) -> tuple[ClassRecord, ...]:
        name = source.strip() or "Empty"
        imports = ("b.B",) if name == "A" else ()
        return (ClassRecord(
            fqn=f"{prefix}.{name}", bases=(), methods=(), fields=(),
            imports=imports, decorators=(),
        ),)


def test_walk_is_sorted_glob_scoped_and_graph_is_resolved(tmp_path: Path) -> None:
    (tmp_path / "b.fake").write_text("B")
    (tmp_path / "a.fake").write_text("A")
    (tmp_path / "c.other").write_text("C")
    catalog = _FakeExtractor().extract(tmp_path)
    assert tuple(r.fqn for r in catalog.classes) == ("a.A", "b.B")
    assert catalog.import_graph == {"a.A": ("b.B",), "b.B": ()}


def test_excluded_dirs_are_skipped(tmp_path: Path) -> None:
    hidden = tmp_path / "tests"
    hidden.mkdir()
    (hidden / "t.fake").write_text("T")
    (tmp_path / "a.fake").write_text("A")
    catalog = _FakeExtractor().extract(tmp_path)
    assert tuple(r.fqn for r in catalog.classes) == ("a.A",)


def test_path_prefix_joins_relative_parts_without_suffix(tmp_path: Path) -> None:
    sub = tmp_path / "src" / "pkg"
    sub.mkdir(parents=True)
    (sub / "mod.fake").write_text("M")
    catalog = _FakeExtractor().extract(tmp_path)
    assert catalog.classes[0].fqn == "src.pkg.mod.M"
