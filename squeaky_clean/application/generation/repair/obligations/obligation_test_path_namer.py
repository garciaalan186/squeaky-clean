"""ObligationTestPathNamer: canonical test-file paths per language."""

import re

from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


class ObligationTestPathNamer:
    """Names the test file an obligation repair should target or create."""

    def invariants_path(
        self, class_name: str, toolkit: LanguageToolkit | None,
    ) -> str | None:
        """Dedicated new test-file path for a class's invariant duties."""
        if toolkit is None:
            return None
        lang = toolkit.language.value
        if lang == "python":
            return f"tests/test_{self.snake(class_name)}_invariants.py"
        if lang in ("typescript", "javascript"):
            ext = "ts" if lang == "typescript" else "js"
            return f"tests/{self.camel(class_name)}Invariants.test.{ext}"
        if lang == "java":
            return f"src/test/java/com/example/{class_name}InvariantsTest.java"
        return None

    def canonical(
        self, class_name: str, toolkit: LanguageToolkit | None,
    ) -> str | None:
        """Canonical new test path for a class with no test file yet."""
        if toolkit is None:
            return None
        lang = toolkit.language.value
        if lang == "python":
            return f"tests/test_{self.snake(class_name)}.py"
        if lang in ("typescript", "javascript"):
            ext = "ts" if lang == "typescript" else "js"
            return f"tests/{self.camel(class_name)}.test.{ext}"
        if lang == "java":
            return f"src/test/java/com/example/{class_name}Test.java"
        return None

    def forms(self, name: str) -> set[str]:
        """All naming forms a test-file stem may use for ``name``."""
        return {name, self.snake(name), self.camel(name)}

    @staticmethod
    def snake(name: str) -> str:
        """snake_case form of a class name."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def camel(self, name: str) -> str:
        """camelCase form of a class name."""
        parts = [p for p in self.snake(name).split("_") if p]
        return parts[0] + "".join(p.title() for p in parts[1:]) if parts else name
