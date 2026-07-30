"""JavaIntegrationBootstrap: writes pom.xml for Maven-based Java projects."""

from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_POM_XML: str = """\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 \
http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.cleanagent</groupId>
    <artifactId>generated</artifactId>
    <version>1.0-SNAPSHOT</version>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
            </plugin>
        </plugins>
    </build>
</project>
"""


class JavaIntegrationBootstrap(IntegrationBootstrap):
    """Writes a Maven pom.xml and creates source directories for Java projects."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Create Maven directory layout and ``pom.xml`` at the project root.

        Maven expects ``src/main/java/`` for production sources and
        ``src/test/java/`` for test sources. The ``pom.xml`` declares
        a JUnit 5 dependency so ``mvn test`` works out of the box.
        """
        self._fs.write(output_dir / "pom.xml", _POM_XML)
