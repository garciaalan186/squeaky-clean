"""Tests for build_manifest_helpers: install-package parsing + dep stanzas."""

from squeaky_clean.application.generation.integration.manifests.build_manifest_helpers import (
    is_spring_technology,
    parse_install_package,
    render_dependency,
    render_managed_dependency,
    render_test_dependency,
)


def test_parse_explicit_gav_triple_strips_whitespace() -> None:
    assert parse_install_package(" org.acme : acme-core : 1.2.3 ") == (
        "org.acme", "acme-core", "1.2.3",
    )


def test_parse_pip_shape_resolves_group_id_from_registry() -> None:
    gid, aid, ver = parse_install_package("jackson-databind==2.15.2")
    assert (gid, aid, ver) == ("com.fasterxml.jackson.core", "jackson-databind", "2.15.2")


def test_parse_unknown_artifact_falls_back_to_example_group_and_latest() -> None:
    assert parse_install_package("mystery-lib") == ("com.example", "mystery-lib", "LATEST")


def test_rendered_stanzas_cover_versioned_managed_and_test_shapes() -> None:
    versioned = render_dependency("org.acme", "acme-core", "1.2.3")
    assert "<groupId>org.acme</groupId>" in versioned
    assert "<version>1.2.3</version>" in versioned
    managed = render_managed_dependency("org.acme", "acme-core")
    assert "<artifactId>acme-core</artifactId>" in managed
    assert "<version>" not in managed
    test_dep = render_test_dependency()
    assert "<artifactId>junit-jupiter</artifactId>" in test_dep
    assert "<scope>test</scope>" in test_dep
    assert is_spring_technology("spring_boot")
