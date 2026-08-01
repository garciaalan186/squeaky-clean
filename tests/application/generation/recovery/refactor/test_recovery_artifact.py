"""Tests for RecoveryArtifact: the faithful, re-analyzable recovery output."""

import dataclasses

import pytest

from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.refactor.recovery_artifact import (
    RecoveryArtifact,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _artifact() -> RecoveryArtifact:
    record = ClassRecord(
        fqn="app.user.User", bases=(), methods=("rename(name)",),
        fields=(), imports=(), decorators=(),
    )
    module = ModuleSpec(
        name="App", layer=LayerType.DOMAIN, exports=(), depends=(),
        classes=(ClassSpec(
            name="User", pattern="Entity", implements=None,
            methods=(), depends=(), concretes=(),
        ),),
        invariants=(),
    )
    return RecoveryArtifact(
        catalog=ClassCatalog(classes=(record,), import_graph={"app.user.User": ()}),
        layers={"app.user.User": LayerType.DOMAIN},
        spec=ArchitectureSpec.single(module),
    )


def test_artifact_bundles_catalog_layers_and_spec_unchanged() -> None:
    artifact = _artifact()
    assert artifact.catalog.classes[0].fqn == "app.user.User"
    assert artifact.layers["app.user.User"] is LayerType.DOMAIN
    assert artifact.spec.modules[0].classes[0].name == "User"


def test_identical_artifacts_compare_equal() -> None:
    assert _artifact() == _artifact()


def test_artifact_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(_artifact(), "layers", {})  # noqa: B010
