"""Static XML stanza templates for BuildManifestGenerator."""

from __future__ import annotations

PARENT: str = (
    "    <parent>\n"
    "        <groupId>org.springframework.boot</groupId>\n"
    "        <artifactId>spring-boot-starter-parent</artifactId>\n"
    "        <version>2.7.18</version>\n"
    "        <relativePath/>\n"
    "    </parent>\n"
)

_COMPILER_PLUGIN: str = (
    "            <plugin>\n"
    "                <groupId>org.apache.maven.plugins</groupId>\n"
    "                <artifactId>maven-compiler-plugin</artifactId>\n"
    "                <version>3.13.0</version>\n"
    "                <configuration>\n"
    "                    <release>11</release>\n"
    "                </configuration>\n"
    "            </plugin>\n"
)

SPRING_BUILD: str = (
    "    <build>\n        <plugins>\n"
    + _COMPILER_PLUGIN
    + "            <plugin>\n"
    "                <groupId>org.springframework.boot</groupId>\n"
    "                <artifactId>spring-boot-maven-plugin</artifactId>\n"
    "            </plugin>\n"
    "            <plugin>\n"
    "                <groupId>org.apache.maven.plugins</groupId>\n"
    "                <artifactId>maven-surefire-plugin</artifactId>\n"
    "                <version>3.2.5</version>\n"
    "            </plugin>\n"
    "        </plugins>\n    </build>\n"
)

PLAIN_BUILD: str = (
    "    <build>\n        <plugins>\n"
    + _COMPILER_PLUGIN
    + "            <plugin>\n"
    "                <groupId>org.apache.maven.plugins</groupId>\n"
    "                <artifactId>maven-surefire-plugin</artifactId>\n"
    "                <version>3.2.5</version>\n"
    "            </plugin>\n"
    "        </plugins>\n    </build>\n"
)

POM_TEMPLATE: str = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
{parent}    <groupId>com.example</groupId>
    <artifactId>{slug}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <properties>
        <java.version>11</java.version>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
{dependencies}
    </dependencies>
{build}</project>
"""
