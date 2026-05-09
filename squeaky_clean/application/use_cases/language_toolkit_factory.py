"""LanguageToolkitFactory: build a LanguageToolkit for a given TargetLanguage."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class LanguageToolkitFactory:
    """Resolves a TargetLanguage to its concrete LanguageToolkit."""

    def for_language(self, lang: TargetLanguage) -> LanguageToolkit:
        """Return the LanguageToolkit describing `lang`'s conventions."""
        if lang is TargetLanguage.PYTHON:
            return LanguageToolkit(
                language=TargetLanguage.PYTHON,
                file_extension=".py",
                test_file_prefix="test_",
                test_file_suffix=".py",
                icp_library="python",
                architect_library="python",
                identifier_case="snake",
                test_framework_imports="import pytest",
                error_types_tuple="(ValueError, ZeroDivisionError)",
                assert_eq_template="assert {actual} == {expected}",
                assert_raises_template="with pytest.raises({errs}): {body}",
                array_type_template="list[{T}]",
                method_signature_style="snake",
            )
        if lang is TargetLanguage.JAVASCRIPT:
            return LanguageToolkit(
                language=TargetLanguage.JAVASCRIPT,
                file_extension=".js",
                test_file_prefix="",
                test_file_suffix=".test.js",
                icp_library="javascript",
                architect_library="javascript",
                identifier_case="camel",
                test_framework_imports=(
                    "import { test } from 'node:test';\n"
                    "import assert from 'node:assert/strict';"
                ),
                error_types_tuple="Error",
                assert_eq_template="assert.strictEqual({actual}, {expected});",
                assert_raises_template="assert.throws(() => {{ {body} }}, {errs});",
                array_type_template="{T}[]",
                method_signature_style="camel",
            )
        if lang is TargetLanguage.TYPESCRIPT:
            return LanguageToolkit(
                language=TargetLanguage.TYPESCRIPT,
                file_extension=".ts",
                test_file_prefix="",
                test_file_suffix=".test.ts",
                icp_library="typescript",
                architect_library="typescript",
                identifier_case="camel",
                test_framework_imports=(
                    "import { test } from 'node:test';\n"
                    "import assert from 'node:assert/strict';"
                ),
                error_types_tuple="Error",
                assert_eq_template="assert.strictEqual({actual}, {expected});",
                assert_raises_template="assert.throws(() => {{ {body} }}, {errs});",
                array_type_template="{T}[]",
                method_signature_style="camel",
            )
        if lang is TargetLanguage.JAVA:
            return LanguageToolkit(
                language=TargetLanguage.JAVA,
                file_extension=".java",
                test_file_prefix="",
                test_file_suffix="Test.java",
                icp_library="java",
                architect_library="java",
                identifier_case="pascal",
                source_subdir="src/main/java",
                test_subdir="src/test/java",
                test_framework_imports=(
                    "import org.junit.jupiter.api.Test;\n"
                    "import static org.junit.jupiter.api.Assertions.*;"
                ),
                error_types_tuple="IllegalArgumentException.class",
                assert_eq_template="assertEquals({expected}, {actual});",
                assert_raises_template="assertThrows({errs}, () -> {{ {body} }});",
                array_type_template="{T}[]",
                method_signature_style="camel",
            )
        if lang is TargetLanguage.GO:
            return LanguageToolkit(
                language=TargetLanguage.GO,
                file_extension=".go",
                test_file_prefix="",
                test_file_suffix="_test.go",
                icp_library="go",
                architect_library="go",
                identifier_case="camel",
                test_framework_imports="import \"testing\"",
                error_types_tuple="error",
                assert_eq_template="if {actual} != {expected} {{ t.Fatalf(\"want %v got %v\", {expected}, {actual}) }}",
                assert_raises_template="if err := func() (err error) {{ defer func() {{ if r := recover(); r != nil {{ err = fmt.Errorf(\"%v\", r) }} }}(); {body}; return nil }}(); err == nil {{ t.Fatal(\"expected error\") }}",
                array_type_template="[]{T}",
                method_signature_style="camel",
            )
        if lang is TargetLanguage.RUST:
            return LanguageToolkit(
                language=TargetLanguage.RUST,
                file_extension=".rs",
                test_file_prefix="",
                test_file_suffix=".rs",
                icp_library="rust",
                architect_library="rust",
                identifier_case="snake",
                test_framework_imports="#[cfg(test)] use super::*;",
                error_types_tuple="String",
                assert_eq_template="assert_eq!({actual}, {expected});",
                assert_raises_template="assert!(std::panic::catch_unwind(|| {{ {body} }}).is_err());",
                array_type_template="Vec<{T}>",
                method_signature_style="snake",
            )
        raise ValueError(f"unsupported TargetLanguage: {lang}")
