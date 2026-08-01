"""Tests for IntegrationFileWriter: path resolution and __init__.py seeding."""

from pathlib import Path

from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.integration.integration_file_writer import (
    IntegrationFileWriter,
)
from squeaky_clean.application.generation.testgen.test_skeleton import TestSkeleton
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class _FakeFileSystem(ProjectFileSystem):
    """Write-through fake: real tmp files so the writer's exists() checks work."""

    def read(self, path: Path) -> str:
        return path.read_text()

    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def list_files(self, root: Path) -> list[Path]:
        return [p for p in root.rglob("*") if p.is_file()]


def _impl(path: str) -> ImplementedClass:
    return ImplementedClass(class_name="User", file_path=path,
                            code="class User: ...", test_code=None,
                            cost_usd=0.0, duration_ms=0,
                            input_tokens=0, output_tokens=0)


def test_write_class_writes_under_output_dir_and_seeds_module_init(tmp_path: Path) -> None:
    writer = IntegrationFileWriter(_FakeFileSystem())
    target = writer.write_class(_impl("src/domain/auth/user.py"), tmp_path)
    assert target == tmp_path / "src" / "domain" / "auth" / "user.py"
    assert target.read_text() == "class User: ..."
    assert (tmp_path / "src" / "domain" / "auth" / "__init__.py").exists()


def test_absolute_path_is_rebased_onto_its_src_suffix(tmp_path: Path) -> None:
    writer = IntegrationFileWriter(_FakeFileSystem())
    target = writer.write_class(_impl("/elsewhere/src/domain/auth/user.py"), tmp_path)
    assert target == tmp_path / "src" / "domain" / "auth" / "user.py"


def test_shallow_layout_gets_no_init_seeding(tmp_path: Path) -> None:
    writer = IntegrationFileWriter(_FakeFileSystem())
    target = writer.write_class(_impl("src/user.py"), tmp_path)
    assert target == tmp_path / "src" / "user.py"
    # Outer roots are the IntegrationBootstrap's job; nothing seeded here.
    assert not (tmp_path / "src" / "__init__.py").exists()


def test_write_test_resolves_tests_marker_and_seeds_init(tmp_path: Path) -> None:
    skeleton = TestSkeleton(class_name="User",
                            file_path="tests/domain/auth/test_user.py",
                            code="def test_user() -> None: ...")
    target = IntegrationFileWriter(_FakeFileSystem()).write_test(skeleton, tmp_path)
    assert target == tmp_path / "tests" / "domain" / "auth" / "test_user.py"
    assert target.read_text() == "def test_user() -> None: ..."
    assert (tmp_path / "tests" / "domain" / "auth" / "__init__.py").exists()
