"""TypeScriptIntegrationBootstrap: writes package.json and tsconfig.json for TS projects."""

import json
from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_PACKAGE_JSON: str = json.dumps(
    {
        "type": "module",
        "devDependencies": {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
        },
    },
    indent=2,
) + "\n"

_TSCONFIG_JSON: str = json.dumps(
    {
        "compilerOptions": {
            "target": "ES2022",
            "module": "nodenext",
            "moduleResolution": "nodenext",
            "strict": True,
            "outDir": "dist",
            "rootDir": ".",
            "declaration": False,
            "esModuleInterop": True,
            "skipLibCheck": True,
        },
        "include": ["src/**/*.ts", "tests/**/*.ts"],
    },
    indent=2,
) + "\n"


class TypeScriptIntegrationBootstrap(IntegrationBootstrap):
    """Writes package.json and tsconfig.json so TypeScript projects compile and run."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Create ``package.json`` and ``tsconfig.json`` at the project root.

        The package.json declares ES module type and TypeScript dev
        dependencies. The tsconfig.json configures nodenext module
        resolution, strict mode, and output to the ``dist/`` directory.
        """
        self._fs.write(output_dir / "package.json", _PACKAGE_JSON)
        self._fs.write(output_dir / "tsconfig.json", _TSCONFIG_JSON)
