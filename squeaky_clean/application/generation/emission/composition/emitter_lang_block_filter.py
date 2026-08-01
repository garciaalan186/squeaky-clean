"""EmitterLangBlockFilter: resolve {{#lang:...}} blocks in a shared template."""


class EmitterLangBlockFilter:
    """Keeps or drops language-conditional blocks in an emitter template.

    Syntax (line-based): a line ``{{#lang:java}}`` or ``{{#lang:js,ts}}``
    opens a block, ``{{/lang}}`` closes it. Inner lines survive only when
    the composing language appears in the opener's comma list. The marker
    lines themselves never survive. Blocks do not nest (R6.1a keeps the
    template grammar deliberately flat).
    """

    _OPEN = "{{#lang:"
    _CLOSE = "{{/lang}}"

    def filter(self, text: str, language: str) -> str:
        """Return ``text`` with only ``language``'s conditional blocks kept."""
        out: list[str] = []
        keeping = True
        in_block = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(self._OPEN) and stripped.endswith("}}"):
                langs = stripped[len(self._OPEN):-2].split(",")
                keeping = language in tuple(lang.strip() for lang in langs)
                in_block = True
                continue
            if stripped == self._CLOSE:
                keeping = True
                in_block = False
                continue
            if keeping or not in_block:
                out.append(line)
        return "\n".join(out) + ("\n" if text.endswith("\n") else "")
