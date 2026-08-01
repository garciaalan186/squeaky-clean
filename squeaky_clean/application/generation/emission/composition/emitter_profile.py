"""EmitterProfile: named language-delta blocks for shared emitter templates."""

from __future__ import annotations


class EmitterProfile:
    """One language's delta blocks, parsed from ``_shared/profiles/<lang>.md``.

    A profile file is markdown where every ``## <block_name>`` heading opens
    a named block whose body runs until the next heading. Templates pull a
    block in with ``{{profile:<block_name>}}``. Unknown references are left
    literal (same introspection convention as ComposeAgentSpec).
    """

    def __init__(self, blocks: dict[str, str]) -> None:
        self._blocks: dict[str, str] = blocks

    @classmethod
    def from_markdown(cls, text: str) -> EmitterProfile:
        """Parse ``## name`` sections into named blocks."""
        blocks: dict[str, str] = {}
        name: str | None = None
        body: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                if name is not None:
                    blocks[name] = "\n".join(body).strip()
                name = line[3:].strip()
                body = []
            elif name is not None:
                body.append(line)
        if name is not None:
            blocks[name] = "\n".join(body).strip()
        return cls(blocks)

    def substitute(self, text: str) -> str:
        """Replace every ``{{profile:<name>}}`` with its block body."""
        out = text
        for name, body in self._blocks.items():
            out = out.replace(f"{{{{profile:{name}}}}}", body)
        return out
