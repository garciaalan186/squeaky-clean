"""Tests for micro_eval_scaffold (R5.4)."""

import json

from squeaky_clean.interface.cli.micro_eval_scaffold import (
    EXTRA_FILES,
    LANGUAGES,
    compilers,
)


def test_compilers_cover_every_micro_eval_language() -> None:
    assert set(compilers()) == {lang.value for lang in LANGUAGES}


def test_typescript_scaffold_is_valid_json() -> None:
    ts = EXTRA_FILES["typescript"]
    tsconfig = json.loads(ts["tsconfig.json"])
    assert tsconfig["compilerOptions"]["noEmit"] is True
    assert json.loads(ts["package.json"])["type"] == "module"
