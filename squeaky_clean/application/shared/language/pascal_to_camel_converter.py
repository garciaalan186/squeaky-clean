"""PascalToCamelConverter: PascalCase identifier -> camelCase."""


class PascalToCamelConverter:
    """Converts a PascalCase identifier to camelCase by lowering the first letter."""

    def convert(self, pascal: str) -> str:
        """Return the camelCase form of ``pascal``.

        Empty input returns empty. Leading acronyms like ``HTTPClient``
        become ``httpClient`` — all leading upper-case letters collapse
        to lower-case until the first letter that begins a new word.
        """
        if not pascal:
            return ""
        if len(pascal) == 1:
            return pascal.lower()
        if pascal[0].islower():
            return pascal
        if pascal[1].islower():
            return pascal[0].lower() + pascal[1:]
        return self._lower_acronym(pascal)

    def _lower_acronym(self, pascal: str) -> str:
        idx = 0
        while idx < len(pascal) and pascal[idx].isupper():
            idx += 1
        if idx == len(pascal):
            return pascal.lower()
        split = idx - 1
        return pascal[:split].lower() + pascal[split:]
