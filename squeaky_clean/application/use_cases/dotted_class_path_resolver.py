"""DottedClassPathResolver: per-language dotted path for a class+module pair."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class DottedClassPathResolver:
    """Compute the canonical import/dotted-path for a class under ``toolkit``.

    The path matches what ``AssignPatternsPaths`` actually emits to disk so
    that TestArchitect imports always resolve. One entry-point method:
    ``resolve(class_spec, module_spec)``.
    """

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit: LanguageToolkit = toolkit
        self._snake: SnakeCaseConverter = SnakeCaseConverter()
        self._camel: PascalToCamelConverter = PascalToCamelConverter()

    def resolve(self, class_spec: ClassSpec, module_spec: ModuleSpec) -> str:
        """Return the dotted-path string for ``class_spec`` in ``module_spec``."""
        lang = self._toolkit.language
        name = class_spec.name
        if lang is TargetLanguage.PYTHON:
            return self._python(name, module_spec)
        if lang is TargetLanguage.JAVA:
            return f"com.example.{name}"
        if lang is TargetLanguage.GO:
            return name
        if lang is TargetLanguage.RUST:
            return f"crate::{self._snake.convert(name)}"
        if lang in (TargetLanguage.JAVASCRIPT, TargetLanguage.TYPESCRIPT):
            return f"./src/{self._camel.convert(name)}"
        return name

    def _python(self, class_name: str, module: ModuleSpec) -> str:
        layer = module.layer.value.lower()
        mod_slug = self._snake.convert(module.name)
        stem = self._snake.convert(class_name)
        return f"src.{layer}.{mod_slug}.{stem}"
