"""SpecConformanceChecker: verify generated classes expose Squib methods."""

import re

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation


class SpecConformanceChecker:
    """Flags generated classes that dropped/renamed a Squib-declared method.

    The TestArchitect binds acceptance tests to the method names the
    architect declared in the Squib; when an ICP emits a different name
    (e.g. a framework-canonical ``handle`` instead of the declared
    ``handlePost``), tests call a method that does not exist. This check
    measures that drift so it is visible (spec_conformance_violations)
    rather than surfacing only as an opaque test/compile failure.
    """

    def check(self, impl: ModuleImplementation) -> tuple[str, ...]:
        """Return one message per declared method absent from its class."""
        code_by_name = {c.class_name: c.code for c in impl.implemented_classes}
        out: list[str] = []
        for spec in impl.module.classes:
            code = code_by_name.get(spec.name)
            if code is None:
                continue
            for sig in spec.methods:
                name = sig.split("(")[0].strip()
                if name and not self._present(name, code):
                    out.append(
                        f"{spec.name} missing declared method '{name}'")
        return tuple(out)

    def _present(self, name: str, code: str) -> bool:
        for form in self._forms(name):
            if re.search(rf"\b{re.escape(form)}\s*\(", code):
                return True
        return False

    @staticmethod
    def _forms(name: str) -> set[str]:
        """Naming-convention variants (raw / snake / camel) of a method name.

        Comparison is convention-agnostic so a Squib ``findById`` matches a
        Python ``find_by_id`` and vice-versa, avoiding false positives from
        the ICP's language translation.
        """
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        parts = [p for p in snake.split("_") if p]
        camel = parts[0] + "".join(p.title() for p in parts[1:]) if parts else name
        return {name, snake, camel}
