"""Helpers for BuildManifestGenerator: parse + dep stanza renderer."""

from __future__ import annotations

from squeaky_clean.application.use_cases.build_manifest_registry import (
    is_spring_tech,
    lookup_group_id,
)


def parse_install_package(raw: str) -> tuple[str, str, str]:
    """Parse ``groupId:artifactId:version`` or ``artifactId==version``.

    Returns ``(group_id, artifact_id, version)``. Falls back to the
    static groupId registry when the raw value is in the
    ``artifactId==version`` shape (no explicit groupId).
    """
    if ":" in raw and raw.count(":") >= 2:
        gid, aid, ver = raw.split(":", 2)
        return gid.strip(), aid.strip(), ver.strip()
    aid, _, ver = raw.partition("==")
    aid = aid.strip()
    ver = ver.strip() or "LATEST"
    gid = lookup_group_id(aid) or "com.example"
    return gid, aid, ver


def is_spring_technology(tech: str) -> bool:
    """Return True iff ``tech`` denotes a Spring-managed technology."""
    return is_spring_tech(tech)


def render_dependency(group_id: str, artifact_id: str, version: str) -> str:
    """Render one ``<dependency>`` XML stanza."""
    return (
        "        <dependency>\n"
        f"            <groupId>{group_id}</groupId>\n"
        f"            <artifactId>{artifact_id}</artifactId>\n"
        f"            <version>{version}</version>\n"
        "        </dependency>"
    )


def render_managed_dependency(group_id: str, artifact_id: str) -> str:
    """Render a ``<dependency>`` whose version is managed by the parent BOM."""
    return (
        "        <dependency>\n"
        f"            <groupId>{group_id}</groupId>\n"
        f"            <artifactId>{artifact_id}</artifactId>\n"
        "        </dependency>"
    )


def render_test_dependency() -> str:
    """Render the JUnit 5 test dependency stanza (always present)."""
    return (
        "        <dependency>\n"
        "            <groupId>org.junit.jupiter</groupId>\n"
        "            <artifactId>junit-jupiter</artifactId>\n"
        "            <version>5.10.0</version>\n"
        "            <scope>test</scope>\n"
        "        </dependency>"
    )
