"""Tests for EmitterProfile block parsing and substitution."""

from squeaky_clean.application.generation.emission.composition.emitter_profile import EmitterProfile

_PROFILE = """# Language Profile: Example

## fence_tag
python

## error_rule
Raise `ValueError` for invalid inputs.

## empty_block

"""


def test_parses_blocks_by_heading() -> None:
    profile = EmitterProfile.from_markdown(_PROFILE)
    text = profile.substitute("use {{profile:fence_tag}} fences")
    assert text == "use python fences"


def test_multiline_and_empty_blocks() -> None:
    profile = EmitterProfile.from_markdown(_PROFILE)
    assert profile.substitute("{{profile:error_rule}}").startswith("Raise")
    assert profile.substitute("x{{profile:empty_block}}y") == "xy"


def test_unknown_references_stay_literal() -> None:
    profile = EmitterProfile.from_markdown(_PROFILE)
    assert profile.substitute("{{profile:nope}}") == "{{profile:nope}}"
