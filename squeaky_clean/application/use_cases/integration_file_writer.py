"""IntegrationFileWriter: writes one ImplementedClass or TestSkeleton to disk."""

from pathlib import Path

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton
from squeaky_clean.application.use_cases.java_packageize import java_packageize
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_LAYERS: frozenset[str] = frozenset(
    {"domain", "application", "infrastructure", "interface"},
)


class IntegrationFileWriter:
    """Writes one class/test file via ProjectFileSystem under an output root."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def write_class(self, impl: ImplementedClass, output_dir: Path) -> Path:
        """Write ``impl.code`` under ``output_dir`` and return the path.

        Honors the file_path the upstream assignment recorded on
        ``impl`` — expected to be relative to the project root
        (e.g. ``src/domain/auth/user.py``). Absolute paths are rebased
        under ``output_dir`` using only their ``src/...`` / ``tests/...``
        suffix for safety. Seeds ``__init__.py`` along intermediate
        package directories for Python layered layouts.
        """
        target = self._resolve(impl.file_path, output_dir)
        self._fs.write(target, impl.code)
        self._seed_module_init(target, output_dir)
        return target

    def write_test(self, skeleton: TestSkeleton, output_dir: Path) -> Path:
        """Write ``skeleton.code`` under ``output_dir`` and return the path."""
        target = self._resolve(skeleton.file_path, output_dir)
        self._fs.write(target, skeleton.code)
        self._seed_module_init(target, output_dir)
        return target

    def _resolve(self, raw: str, output_dir: Path) -> Path:
        candidate = Path(raw)
        parts = candidate.parts
        for marker in ("src", "tests"):
            if marker in parts:
                idx = parts.index(marker)
                target = output_dir.joinpath(*parts[idx:])
                return java_packageize(target, output_dir)
        return java_packageize(output_dir / candidate, output_dir)

    def _seed_module_init(self, target: Path, output_dir: Path) -> None:
        """Create ``__init__.py`` for the module subdir of a layered file.

        Triggers only when ``target`` lives at
        ``<output_dir>/<src|tests>/<layer>/<module>/<file>.py``. The
        outer roots (``src/``, ``src/<layer>/``) are seeded once by the
        IntegrationBootstrap. This method handles the per-module dir.
        """
        if target.suffix != ".py":
            return
        try:
            rel = target.relative_to(output_dir)
        except ValueError:
            return
        parts = rel.parts
        if len(parts) < 4:
            return
        if parts[0] not in {"src", "tests"} or parts[1] not in _LAYERS:
            return
        module_dir = output_dir / parts[0] / parts[1] / parts[2]
        init = module_dir / "__init__.py"
        if not init.exists():
            self._fs.write(init, "")
