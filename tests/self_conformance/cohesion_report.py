"""Advisory package-cohesion signal (R6.11a): intra-package import ratio.

A package whose modules never import each other is a pile, not a
component. This is REPORTED, not gated — run it for the table:

    python3 tests/self_conformance/cohesion_report.py

Ratio = (imports of same-package siblings) / (all squeaky_clean-internal
imports made by the package's modules). Gate later only if the signal
proves meaningful (per the R6.11 one-quarter observation window).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Allow running as a plain script: put the repo root on sys.path so the
# first-party `tests` package resolves (same bootstrap as regenerate_baseline).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.self_conformance.conformance_scan import package_root  # noqa: E402

_PKG = "squeaky_clean"


def _module_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
        elif isinstance(node, ast.Import):
            out.extend(alias.name for alias in node.names)
    return [name for name in out if name.startswith(_PKG)]


def intra_package_import_ratios() -> dict[str, tuple[int, int, float]]:
    """Per package: (intra_imports, internal_imports, ratio), sorted."""
    root = package_root()
    ratios: dict[str, tuple[int, int, float]] = {}
    for pkg_dir in sorted(p.parent for p in root.rglob("__init__.py")):
        modules = [p for p in pkg_dir.glob("*.py") if p.name != "__init__.py"]
        if len(modules) < 2:
            continue
        pkg_name = ".".join(pkg_dir.relative_to(root.parent).parts)
        intra = internal = 0
        for module in modules:
            for imported in _module_imports(module):
                internal += 1
                if imported.rpartition(".")[0] == pkg_name:
                    intra += 1
        ratio = (intra / internal) if internal else 0.0
        rel = str(pkg_dir.relative_to(root.parent))
        ratios[rel] = (intra, internal, round(ratio, 3))
    return ratios


def main() -> None:
    """Print the advisory cohesion table, least-cohesive first."""
    rows = sorted(intra_package_import_ratios().items(), key=lambda kv: kv[1][2])
    print(f"{'package':60} intra/internal  ratio")
    for pkg, (intra, internal, ratio) in rows:
        print(f"{pkg:60} {intra:>5}/{internal:<8} {ratio:.3f}")


if __name__ == "__main__":
    main()
