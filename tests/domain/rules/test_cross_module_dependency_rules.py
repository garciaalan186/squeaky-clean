"""Tests for cross_module_dependency_rules (domain home of the R6.6c move).

The full behavioral matrix lives in
tests/application/use_cases/test_validate_cross_module_dependencies.py,
which now exercises the same rules through the application seam; this file
pins the domain function and the ArchitectureSpec entity method directly.
"""

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.rules.cross_module_dependency_rules import (
    collect_cross_module_violations,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, depends: tuple[str, ...] = ()) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="SimpleClass", implements=None,
        methods=(), depends=depends, concretes=(),
    )


def _mod(
    name: str, *,
    classes: tuple[ClassSpec, ...],
    exports: tuple[str, ...] = (),
    depends: tuple[str, ...] = (),
) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=LayerType.DOMAIN, exports=exports,
        depends=depends, classes=classes, invariants=(),
    )


def _arch(*modules: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(
        modules=modules, graph=ArchitectureGraph(edges={}),
    )


def test_clean_architecture_no_violations() -> None:
    repo = _mod("Repo", classes=(_cls("UserRepo"),), exports=("UserRepo",))
    app = _mod(
        "App", classes=(_cls("Login", depends=("Repo::UserRepo",)),),
        depends=("Repo",),
    )
    assert collect_cross_module_violations(_arch(repo, app)) == ()


def test_missing_depends_produces_violation_string() -> None:
    repo = _mod("Repo", classes=(_cls("UserRepo"),), exports=("UserRepo",))
    app = _mod("App", classes=(_cls("Login", depends=("Repo::UserRepo",)),))
    out = collect_cross_module_violations(_arch(repo, app))
    assert out == (
        "module 'App' class 'Login' dep 'Repo::UserRepo': target module "
        "'Repo' not in importing module's DEPENDS list",
    )


def test_unexported_type_flagged() -> None:
    repo = _mod("Repo", classes=(_cls("UserRepo"),))
    app = _mod(
        "App", classes=(_cls("Login", depends=("Repo::UserRepo",)),),
        depends=("Repo",),
    )
    out = collect_cross_module_violations(_arch(repo, app))
    assert len(out) == 1
    assert "EXPORTS" in out[0]


def test_entity_method_delegates_to_rules() -> None:
    app = _mod("App", classes=(_cls("Login", depends=("Ghost::X",)),))
    spec = _arch(app)
    assert spec.cross_module_dep_violations() == (
        collect_cross_module_violations(spec)
    )
    assert any("unknown module" in v for v in spec.cross_module_dep_violations())
