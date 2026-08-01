"""Tests for build_manifest_templates: static pom.xml stanza templates."""

from squeaky_clean.application.generation.integration.manifests.build_manifest_templates import (
    PARENT,
    PLAIN_BUILD,
    POM_TEMPLATE,
    SPRING_BUILD,
)


def test_pom_template_formats_all_four_placeholders() -> None:
    pom = POM_TEMPLATE.format(parent=PARENT, slug="cart-service",
                              dependencies="        <!-- deps -->",
                              build=PLAIN_BUILD)
    assert pom.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<artifactId>cart-service</artifactId>" in pom
    assert "<artifactId>spring-boot-starter-parent</artifactId>" in pom
    assert "{parent}" not in pom and "{slug}" not in pom
    assert "{dependencies}" not in pom and "{build}" not in pom


def test_spring_build_adds_boot_plugin_on_top_of_plain_build() -> None:
    assert "spring-boot-maven-plugin" in SPRING_BUILD
    assert "spring-boot-maven-plugin" not in PLAIN_BUILD
    for build in (SPRING_BUILD, PLAIN_BUILD):
        assert "maven-compiler-plugin" in build
        assert "maven-surefire-plugin" in build


def test_parent_stanza_pins_the_boot_parent_bom() -> None:
    assert "<groupId>org.springframework.boot</groupId>" in PARENT
    assert "<version>2.7.18</version>" in PARENT
    assert "<relativePath/>" in PARENT
