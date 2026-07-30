"""PackageCohesionRule: CCP + package-granularity checks (R1.7)."""

from pathlib import Path

from squeaky_clean.domain.value_objects.violation import Violation

_MAX_MODULES = 20
_CATCHALL = frozenset(
    {"use_cases", "dtos", "helpers", "utils", "misc", "common"}
)


class PackageCohesionRule:
    """Flags packages that are too large or are type-named catch-alls.

    Component Cohesion Principle: a package is one named capability, not a
    junk drawer. Caps direct modules per package at 20 (the file-count
    analogue of the granularity rule) and forbids type-named packages
    (``use_cases/``, ``dtos/``, ``helpers/``, ``utils/``).
    """

    _NAME = "PackageCohesionRule"

    def check_tree(self, root: Path) -> list[Violation]:
        """Return cohesion violations for every package under ``root``."""
        out: list[Violation] = []
        for pkg in self._packages(root):
            out.extend(self._check_package(pkg, root))
        return out

    @staticmethod
    def _packages(root: Path) -> list[Path]:
        return sorted(
            d for d in root.rglob("*")
            if d.is_dir() and "__pycache__" not in d.parts
        )

    def _check_package(self, pkg: Path, root: Path) -> list[Violation]:
        out: list[Violation] = []
        rel = str(pkg.relative_to(root.parent))
        n = sum(1 for f in pkg.glob("*.py") if f.name != "__init__.py")
        if n > _MAX_MODULES:
            out.append(Violation(
                self._NAME, rel, f"package has {n} modules (>{_MAX_MODULES})",
            ))
        if pkg.name in _CATCHALL:
            out.append(Violation(
                self._NAME, rel, f"type-named catch-all package '{pkg.name}'",
            ))
        return out
