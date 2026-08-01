"""R6.8 poor-man's ratchet: no swallow-and-degrade in techspec/manifests.

The R6.8 acceptance is mechanical: zero ``return None`` (or bare ``return``)
inside except blocks and zero silent ``pass`` handlers under the techspec
and manifest subsystems. Deliberately a plain unit test local to these
directories — NOT a conformance-scan rule (the ratchet file pattern is
owned elsewhere this round).

``None`` is still a legal return value in these modules — but only on a
code path that means "not applicable / clean miss", never from inside an
exception handler.
"""

import ast
from pathlib import Path

_PKG = Path(__file__).resolve().parents[2] / "squeaky_clean"
_SCOPES = (
    _PKG / "infrastructure" / "techspec",
    _PKG / "application" / "generation" / "techspec",
    _PKG / "application" / "generation" / "integration" / "manifests",
)


def _is_none_return(node: ast.Return) -> bool:
    value = node.value
    return value is None or (
        isinstance(value, ast.Constant) and value.value is None
    )


def _offences_in(path: Path) -> list[str]:
    out: list[str] = []
    tree = ast.parse(path.read_text())
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
    for handler in handlers:
        if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
            out.append(f"{path}:{handler.lineno}: silent `pass` in except")
        for stmt in handler.body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Return) and _is_none_return(node):
                    out.append(
                        f"{path}:{node.lineno}: return None inside except"
                    )
    return out


def test_zero_swallow_sites_in_techspec_and_manifests() -> None:
    offences: list[str] = []
    for scope in _SCOPES:
        assert scope.is_dir(), f"scan scope vanished: {scope}"
        for path in sorted(scope.rglob("*.py")):
            offences.extend(_offences_in(path))
    assert offences == [], (
        "R6.8 regression — error swallowing reintroduced:\n"
        + "\n".join(f"  {o}" for o in offences)
    )
