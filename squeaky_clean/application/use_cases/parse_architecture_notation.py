"""ParseArchitectureNotation: split multi-MODULE notation into an ArchitectureSpec."""

from __future__ import annotations

import re

from squeaky_clean.application.use_cases.parse_notation import ParseNotation
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError

_MODULE_HEADER_RE = re.compile(r"(?m)^MODULE\s+(\S+)")


class ParseArchitectureNotation:
    """Parse §Notation that may contain one or more MODULE blocks.

    Returns ArchitectureSpec wrapping all parsed modules plus an inferred
    ArchitectureGraph derived from each module's `DEPENDS [Module::Type]`
    entries (the `Module::` prefix names cross-module dependencies).
    """

    def __init__(self) -> None:
        self._inner: ParseNotation = ParseNotation()

    def parse(self, text: str) -> ArchitectureSpec:
        """Return ArchitectureSpec covering every MODULE block in ``text``."""
        chunks = self._split_into_modules(text)
        if not chunks:
            raise NotationParseError("no MODULE blocks found")
        modules: list[ModuleSpec] = [self._inner.parse(c) for c in chunks]
        edges = self._infer_edges(modules)
        return ArchitectureSpec(modules=tuple(modules), graph=edges)

    def _split_into_modules(self, text: str) -> list[str]:
        positions = [m.start() for m in _MODULE_HEADER_RE.finditer(text)]
        if not positions:
            return []
        positions.append(len(text))
        return [
            text[positions[i]:positions[i + 1]].strip()
            for i in range(len(positions) - 1)
        ]

    def _infer_edges(
        self, modules: list[ModuleSpec],
    ) -> ArchitectureGraph:
        edges: dict[str, tuple[str, ...]] = {}
        for m in modules:
            cross: list[str] = []
            for dep in m.depends:
                if "::" in dep:
                    cross.append(dep.split("::", 1)[0])
            edges[m.name] = tuple(dict.fromkeys(cross))
        return ArchitectureGraph(edges=edges)
