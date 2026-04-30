"""SecurityTestAssembler: combine Security ICP outputs into TestSkeletons."""

import re

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_CODE_FENCE = re.compile(
    r"```[A-Za-z0-9_+-]*\s*\n(?P<code>.*?)```",
    re.DOTALL,
)


class SecurityTestAssembler:
    """Assembles Security ICP responses into per-class TestSkeletons."""

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
        """Group ICP responses by target class, return TestArchitecture."""
        grouped: dict[str, list[str]] = {}
        idx = 0
        for concern in concerns:
            if concern.target_class not in class_map:
                continue
            code = self._extract_code(responses[idx].content)
            grouped.setdefault(concern.target_class, []).append(code)
            idx += 1
        skeletons: list[TestSkeleton] = []
        prefix = self._test_dir(module, toolkit)
        for class_name, fragments in grouped.items():
            snake = self._snake.convert(class_name)
            path = f"{prefix}/test_{snake}_security.py"
            combined = "\n\n".join(fragments) + "\n"
            skeletons.append(TestSkeleton(
                class_name=class_name, file_path=path, code=combined,
            ))
        return TestArchitecture(
            gherkin_scenarios=(), test_skeletons=tuple(skeletons),
        )

    def _test_dir(
        self,
        module: ModuleSpec | None,
        toolkit: LanguageToolkit | None,
    ) -> str:
        """Return the test directory prefix (layered for Python, else flat)."""
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
        """Extract code from the first fenced block, or return raw."""
        match = _CODE_FENCE.search(raw)
        if match is None:
            return raw.strip()
        return match.group("code").strip()
