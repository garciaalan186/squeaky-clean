"""FixFailureMapper: maps failing test-file stems to their source classes."""

from pathlib import Path

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class FixFailureMapper:
    """Resolves failing-test stems to the ImplementedClass objects to fix."""

    def __init__(self, language: TargetLanguage) -> None:
        self._language: TargetLanguage = language

    def map(
        self, stems: tuple[str, ...],
        classes: tuple[ImplementedClass, ...],
    ) -> tuple[ImplementedClass, ...]:
        """Return the unique subset of ``classes`` implicated by ``stems``."""
        matched: list[ImplementedClass] = []
        seen: set[str] = set()
        for stem in stems:
            for cls in classes:
                if cls.class_name in seen:
                    continue
                if self._matches(stem, cls):
                    matched.append(cls)
                    seen.add(cls.class_name)
        return tuple(matched)

    def _matches(self, stem: str, cls: ImplementedClass) -> bool:
        src_stem = Path(cls.file_path).stem
        if self._language is TargetLanguage.PYTHON:
            return stem == src_stem or stem == f"test_{src_stem}"
        if self._language in (
            TargetLanguage.JAVASCRIPT, TargetLanguage.TYPESCRIPT,
        ):
            return stem == src_stem
        if self._language is TargetLanguage.JAVA:
            return stem == cls.class_name + "Test"
        return False
