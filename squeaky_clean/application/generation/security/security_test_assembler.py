"""SecurityTestAssembler: emit ONE TestSkeleton per SecurityConcern.

Each concern lands in its own file `test_<class>_security_<concern_slug>.py`
so per-file granularity rules (≤80 lines) hold even when a single class has
multiple concerns. Earlier behaviour concatenated all fragments per class
into one file, which routinely blew the 80-line cap.
"""

import re

from squeaky_clean.application.generation.security.security_concern import SecurityConcern
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_skeleton import TestSkeleton
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.language.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_CODE_FENCE = re.compile(
    r"```[A-Za-z0-9_+-]*\s*\n(?P<code>.*?)```",
    re.DOTALL,
)
_SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


class SecurityTestAssembler:
    """Assembles Security ICP responses into per-concern TestSkeletons."""

    def __init__(self) -> None:
        self._snake: SnakeCaseConverter = SnakeCaseConverter()

    def assemble(
        self,
        responses: tuple[LLMResponse, ...],
        concerns: tuple[SecurityConcern, ...],
        class_map: dict[str, ClassSpec],
        module: ModuleSpec | None = None,
        toolkit: LanguageToolkit | None = None,
    ) -> TestArchitecture:
        """Emit one TestSkeleton per (target_class, concern) pair."""
        prefix = self._test_dir(module, toolkit)
        skeletons: list[TestSkeleton] = []
        slug_seen: dict[tuple[str, str], int] = {}
        idx = 0
        for concern in concerns:
            if concern.target_class not in class_map:
                continue
            extracted = self._extract_code(responses[idx].content)
            idx += 1
            if not extracted.strip():
                # Strict fence (R3.1): a prose-only response is NOT test code —
                # skip it rather than writing prose into a .py file that would
                # break collection of the whole generated suite.
                continue
            code = extracted + "\n"
            class_snake = self._snake.convert(concern.target_class)
            base = self._slug(concern.category)
            key = (class_snake, base)
            slug_seen[key] = slug_seen.get(key, 0) + 1
            slug = base if slug_seen[key] == 1 else f"{base}_{slug_seen[key]}"
            path = f"{prefix}/test_{class_snake}_security_{slug}.py"
            skeletons.append(TestSkeleton(
                class_name=concern.target_class, file_path=path, code=code,
            ))
        return TestArchitecture(
            gherkin_scenarios=(), test_skeletons=tuple(skeletons),
        )

    def _test_dir(
        self,
        module: ModuleSpec | None,
        toolkit: LanguageToolkit | None,
    ) -> str:
        if (
            module is None
            or toolkit is None
            or toolkit.identifier_case != "snake"
        ):
            return "tests"
        layer = module.layer.value.lower()
        mod_slug = self._snake.convert(module.name)
        return f"tests/{layer}/{mod_slug}"

    def _extract_code(self, raw: str) -> str:
        """Fenced code only; empty string when the response is prose (R3.1)."""
        match = _CODE_FENCE.search(raw)
        if match is None:
            return ""
        return match.group("code").strip()

    def _slug(self, value: str) -> str:
        s = _SLUG_NON_ALNUM.sub("_", value.strip().lower()).strip("_")
        return s or "concern"
