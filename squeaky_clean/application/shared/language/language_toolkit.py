"""LanguageToolkit: per-language conventions the framework threads through wiring."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.target_language import TargetLanguage


@dataclass(frozen=True)
class LanguageToolkit:
    """Immutable bundle of language-specific conventions.

    Attributes name the pieces needed to turn a language-agnostic
    ClassSpec into concrete file paths and spec-library lookups.
    Prompt-rendering attributes (`assert_eq_template` etc.) feed the
    shared-spec composition pipeline that replaces per-language .md files.
    """

    language: TargetLanguage
    file_extension: str
    test_file_prefix: str
    test_file_suffix: str
    icp_library: str
    architect_library: str
    identifier_case: str
    source_subdir: str = "src"
    test_subdir: str = "tests"
    test_framework_imports: str = ""
    error_types_tuple: str = "Error"
    assert_eq_template: str = "assert {actual} == {expected}"
    assert_raises_template: str = "with pytest.raises({errs}): {body}"
    array_type_template: str = "{T}[]"
    method_signature_style: str = "snake"
