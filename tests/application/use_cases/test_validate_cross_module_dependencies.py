"""Unit tests for validate_cross_module_dependencies."""

from squeaky_clean.application.use_cases.validate_cross_module_dependencies import (
    validate_cross_module_dependencies,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
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
    auth_repo = _mod(
        "AuthRepository", classes=(_cls("UserRepository"),),
        exports=("UserRepository",),
    )
    auth_app = _mod(
        "AuthApplication",
        classes=(_cls("LoginUseCase",
                       depends=("AuthRepository::UserRepository",)),),
        depends=("AuthRepository",),
    )
    assert validate_cross_module_dependencies(_arch(auth_repo, auth_app)) == ()


def test_module_level_depends_missing() -> None:
    auth_repo = _mod(
        "AuthRepository", classes=(_cls("UserRepository"),),
        exports=("UserRepository",),
    )
    auth_app = _mod(
        "AuthApplication",
        classes=(_cls("LoginUseCase",
                       depends=("AuthRepository::UserRepository",)),),
    )
    out = validate_cross_module_dependencies(_arch(auth_repo, auth_app))
    assert len(out) == 1
    assert "AuthApplication" in out[0]
    assert "DEPENDS" in out[0]


def test_type_not_exported() -> None:
    auth_repo = _mod(
        "AuthRepository", classes=(_cls("UserRepository"),),
        exports=(),
    )
    auth_app = _mod(
        "AuthApplication",
        classes=(_cls("LoginUseCase",
                       depends=("AuthRepository::UserRepository",)),),
        depends=("AuthRepository",),
    )
    out = validate_cross_module_dependencies(_arch(auth_repo, auth_app))
    assert len(out) == 1
    assert "EXPORTS" in out[0]


def test_type_not_declared() -> None:
    auth_repo = _mod(
        "AuthRepository", classes=(_cls("OtherRepo"),),
        exports=("OtherRepo",),
    )
    auth_app = _mod(
        "AuthApplication",
        classes=(_cls("LoginUseCase",
                       depends=("AuthRepository::UserRepository",)),),
        depends=("AuthRepository",),
    )
    out = validate_cross_module_dependencies(_arch(auth_repo, auth_app))
    assert len(out) == 1
    assert "not declared" in out[0]


def test_target_module_does_not_exist() -> None:
    auth_app = _mod(
        "AuthApplication",
        classes=(_cls("LoginUseCase",
                       depends=("Ghost::UserRepository",)),),
        depends=("Ghost",),
    )
    out = validate_cross_module_dependencies(_arch(auth_app))
    assert len(out) == 1
    assert "unknown module" in out[0]


def test_mixed_some_clean_some_violations() -> None:
    auth_repo = _mod(
        "AuthRepository", classes=(_cls("UserRepository"),),
        exports=("UserRepository",),
    )
    other = _mod(
        "Other", classes=(_cls("OK"),), exports=("OK",),
    )
    auth_app = _mod(
        "AuthApplication",
        classes=(
            _cls("Good", depends=("AuthRepository::UserRepository",)),
            _cls("Bad", depends=("Ghost::Type",)),
            _cls("AlsoBad", depends=("Other::OK",)),  # missing DEPENDS to Other
        ),
        depends=("AuthRepository",),
    )
    out = validate_cross_module_dependencies(_arch(auth_repo, other, auth_app))
    assert len(out) == 2
    assert any("Ghost" in v for v in out)
    assert any("Other" in v and "DEPENDS" in v for v in out)


def test_self_referential_intra_module_accepted() -> None:
    mod = _mod(
        "M",
        classes=(
            _cls("A"),
            _cls("B", depends=("M::A",)),
        ),
    )
    assert validate_cross_module_dependencies(_arch(mod)) == ()


def test_self_referential_to_undeclared_class_violation() -> None:
    mod = _mod(
        "M", classes=(_cls("B", depends=("M::Ghost",)),),
    )
    out = validate_cross_module_dependencies(_arch(mod))
    assert len(out) == 1
    assert "self-reference" in out[0]


def test_intra_module_unknown_class_violation() -> None:
    mod = _mod("M", classes=(_cls("B", depends=("Ghost",)),))
    out = validate_cross_module_dependencies(_arch(mod))
    assert len(out) == 1
    assert "intra-module" in out[0]


def test_intra_module_known_class_clean() -> None:
    mod = _mod(
        "M",
        classes=(_cls("A"), _cls("B", depends=("A",))),
    )
    assert validate_cross_module_dependencies(_arch(mod)) == ()
