"""LoadAgentSpec: read an agent prompt markdown file from the spec library."""

from pathlib import Path

_SEARCH_DIRS: tuple[str, ...] = (
    "architects",
    "managers",
)
_QUALIFIED_ROOTS: tuple[str, ...] = ("icps", "architects")


class LoadAgentSpec:
    """Loads the raw markdown of a named agent spec from the prompt library.

    Searches the framework's bundled spec library first, then any
    extra roots passed in (used by F4's custom-pattern extension hook
    so external users can ship ICP specs without forking the framework).
    """

    def __init__(
        self,
        root: Path | None = None,
        extra_roots: tuple[Path, ...] = (),
    ) -> None:
        self._root: Path = root or self._default_root()
        self._extra: tuple[Path, ...] = extra_roots

    def load(self, spec_name: str) -> str:
        """Return the markdown text for the given spec name (without .md)."""
        if "/" in spec_name:
            return self._load_qualified(spec_name)
        for base in (self._root, *self._extra):
            for sub in _SEARCH_DIRS:
                candidate = base / sub / f"{spec_name}.md"
                if candidate.is_file():
                    return candidate.read_text()
        raise FileNotFoundError(f"agent spec not found: {spec_name}")

    def _load_qualified(self, rel_path: str) -> str:
        for base in (self._root, *self._extra):
            for qroot in _QUALIFIED_ROOTS:
                candidate = base / qroot / f"{rel_path}.md"
                if candidate.is_file():
                    return candidate.read_text()
            direct = base / f"{rel_path}.md"
            if direct.is_file():
                return direct.read_text()
        raise FileNotFoundError(f"agent spec not found: {rel_path}")

    def _default_root(self) -> Path:
        here = Path(__file__).resolve()
        return here.parents[2] / "interface" / "agent_specs"
