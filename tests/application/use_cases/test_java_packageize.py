"""Tests for java_packageize: Java files rebased under com/example/."""

from pathlib import Path

from squeaky_clean.application.use_cases.java_packageize import java_packageize


def test_main_java_file_rebased_under_com_example(tmp_path: Path) -> None:
    target = tmp_path / "src" / "main" / "java" / "Foo.java"
    rebased = java_packageize(target, tmp_path)
    assert rebased == tmp_path / "src" / "main" / "java" / "com" / "example" / "Foo.java"


def test_test_java_file_rebased(tmp_path: Path) -> None:
    target = tmp_path / "src" / "test" / "java" / "FooTest.java"
    rebased = java_packageize(target, tmp_path)
    assert rebased == tmp_path / "src" / "test" / "java" / "com" / "example" / "FooTest.java"


def test_layered_java_path_flattened(tmp_path: Path) -> None:
    """A layered §Notation path like src/main/java/domain/foo/Bar.java
    should still flatten down to src/main/java/com/example/Bar.java."""
    target = tmp_path / "src" / "main" / "java" / "domain" / "foo" / "Bar.java"
    rebased = java_packageize(target, tmp_path)
    assert rebased == tmp_path / "src" / "main" / "java" / "com" / "example" / "Bar.java"


def test_python_file_passes_through(tmp_path: Path) -> None:
    target = tmp_path / "src" / "domain" / "foo.py"
    assert java_packageize(target, tmp_path) == target


def test_unknown_root_passes_through(tmp_path: Path) -> None:
    target = tmp_path / "Foo.java"
    assert java_packageize(target, tmp_path) == target
