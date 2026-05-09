"""Tests for validate_composition (H2 TechSpecComposer happy path)."""

from __future__ import annotations

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation
from squeaky_clean.application.use_cases.techspec_composer_validator import (
    validate_composition,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec


def _spec(
    methods: tuple[str, ...] = (),
    depends: tuple[str, ...] = (),
) -> ClassSpec:
    return ClassSpec(
        name="Adapter", pattern="Adapter", implements=None,
        methods=methods, depends=depends, concretes=(),
        fields=(), invariants=(),
    )


def _tech(
    ops: tuple[TechSpecOperation, ...] = (),
    env_vars: tuple[str, ...] = (),
    types: tuple[str, ...] = (),
) -> TechSpec:
    if not ops:
        ops = (_op("noop"),)
    return TechSpec(
        schema_version="v1", category="blob_storage", technology="x",
        version_pin="1.0", language="python",
        install={"manager": "pip", "package": "x==1"},
        imports={"primary": "import x", "types": list(types)},
        client_construction={"code": "self._c = x.Client()"},
        primary_operations=ops,
        auth={"method": "env_credentials", "env_vars": list(env_vars)},
    )


def _op(name: str) -> TechSpecOperation:
    return TechSpecOperation(
        name=name, signature="(k: str) -> None",
        sdk_call=f"self._c.{name}(k)", error_types=("OSError",),
        idempotency="idempotent",
    )


def test_clean_composition_returns_empty() -> None:
    cls = _spec(methods=("put_blob(k: str)", "get_blob(k: str)"))
    tech = _tech(ops=(_op("put_blob"), _op("get_blob")))
    assert validate_composition(cls, tech) == ()


def test_method_not_in_primary_ops_flags_error() -> None:
    """A method whose name DOES match a generic verb but isn't in the
    TechSpec's primary_operations list is flagged."""
    cls = _spec(methods=("put_blob(k: str)", "put_extra(k: str)"))
    tech = _tech(ops=(_op("put_blob"),))
    errs = validate_composition(cls, tech)
    assert any("put_extra" in e for e in errs)


def test_unknown_dep_flags_error() -> None:
    cls = _spec(depends=("RandoType",))
    tech = _tech()
    errs = validate_composition(cls, tech, sibling_names=frozenset({"OK"}))
    assert any("RandoType" in e for e in errs)


def test_sibling_dep_accepted() -> None:
    cls = _spec(depends=("Friend",))
    tech = _tech()
    assert validate_composition(cls, tech, frozenset({"Friend"})) == ()


def test_imported_type_dep_accepted() -> None:
    cls = _spec(depends=("ClientError",))
    tech = _tech(types=("from botocore.exceptions import ClientError",))
    assert validate_composition(cls, tech) == ()


def test_invalid_env_var_flags_error() -> None:
    cls = _spec()
    tech = _tech(env_vars=("lowercase_bad",))
    errs = validate_composition(cls, tech)
    assert any("lowercase_bad" in e for e in errs)


def test_non_generic_verb_skips_op_check() -> None:
    """A method whose name doesn't match a generic verb prefix is not gated."""
    cls = _spec(methods=("authenticate(token: str)",))
    tech = _tech()
    assert validate_composition(cls, tech) == ()
