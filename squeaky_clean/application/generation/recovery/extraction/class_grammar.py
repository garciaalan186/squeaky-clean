"""ClassGrammar: one language's class/method/field declaration regexes."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassGrammar:
    """The regex triple that locates class declarations in one language.

    ``class_re`` must expose named groups ``name``/``base``/``impl``;
    ``method_re`` exposes ``name``/``args``; ``field_re`` exposes
    ``name``/``type``. Shared by the Java and ECMAScript catalog
    extractors, which each define their language's grammar once.
    """

    class_re: re.Pattern[str]
    method_re: re.Pattern[str]
    field_re: re.Pattern[str]
