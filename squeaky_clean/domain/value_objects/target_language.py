"""TargetLanguage: enumerates the programming languages the framework targets."""

from enum import Enum


class TargetLanguage(Enum):
    """Languages the Squeaky Clean framework can emit generated code for."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
