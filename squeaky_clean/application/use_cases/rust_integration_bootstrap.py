"""RustIntegrationBootstrap: ensures src/ exists and writes .gitignore for Rust."""

from pathlib import Path

from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem

_GITIGNORE: str = "target/\nCargo.lock\n"


class RustIntegrationBootstrap(IntegrationBootstrap):
    """Writes a Rust project skeleton (src/, .gitignore) for Cargo-managed crates."""

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def bootstrap(self, output_dir: Path) -> None:
        """Ensure ``<output_dir>/src/`` exists and seed a ``.gitignore``.

        Cargo's manifest (``Cargo.toml``) is emitted separately by
        ``cargo_toml_generator``. This bootstrap only guarantees the
        directory layout Cargo expects (the ``src/`` source root) and
        keeps build artefacts out of source control via ``.gitignore``.
        """
        (output_dir / "src").mkdir(parents=True, exist_ok=True)
        self._fs.write(output_dir / ".gitignore", _GITIGNORE)
