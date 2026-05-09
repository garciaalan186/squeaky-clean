"""AssignPatternsPaths: language-aware src/test file path computation."""

from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class AssignPatternsPaths:
    """Computes (src, test) file paths for one class under the active toolkit."""

    def __init__(self, toolkit: LanguageToolkit, output_root: Path) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._root: Path = output_root
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._camel: PascalToCamelConverter = PascalToCamelConverter()

    def for_class(
        self, class_name: str, module: ModuleSpec | None = None,
    ) -> tuple[Path, Path]:
        """Return (src_path, test_path) for the class using toolkit conventions.

        For Python (snake-case), inserts a layered subdir
        ``<layer>/<module>/`` between source/test root and the file when
        ``module`` is supplied. Other languages keep the existing flat
        layout for now (Java's Maven layout is separately handled).
        """
        stem = self._stem(class_name)
        ext = self._toolkit.file_extension
        layer_subpath = self._layer_subpath(module)
        src_path = (
            self._root / self._toolkit.source_subdir / layer_subpath
            / f"{stem}{ext}"
        )
        test_name = (
            f"{self._toolkit.test_file_prefix}{stem}{self._toolkit.test_file_suffix}"
        )
        test_path = (
            self._root / self._toolkit.test_subdir / layer_subpath / test_name
        )
        return src_path, test_path

    def _layer_subpath(self, module: ModuleSpec | None) -> Path:
        """Return ``<layer>/<module>`` for Python, else empty path."""
        if module is None:
            return Path("")
        if self._toolkit.identifier_case != "snake":
            return Path("")
        layer = module.layer.value.lower()
        mod_slug = self._snake.convert(module.name)
        return Path(layer) / mod_slug

    def _stem(self, class_name: str) -> str:
        if self._toolkit.identifier_case == "snake":
            return self._snake.convert(class_name)
        if self._toolkit.identifier_case == "pascal":
            return class_name
        return self._camel.convert(class_name)
