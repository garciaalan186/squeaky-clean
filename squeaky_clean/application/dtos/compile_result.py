"""CompileResult DTO: parsed outcome of one project-compile subprocess run."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompileResult:
    """Immutable record of a single compile/typecheck subprocess invocation.

    ``ok`` is True when the project compiles cleanly. ``error_count`` is
    parsed from the compiler output. ``offending_stems`` are the source
    file stems (class-file basenames, no extension) implicated by the
    errors, used to drive fixer retries. ``raw_output`` is the full
    stdout+stderr for diagnostic context.
    """

    ok: bool
    error_count: int
    offending_stems: tuple[str, ...]
    raw_output: str
    # Project-relative paths of TEST files with compile errors. These are
    # regenerated against the real source (source-authoritative) rather than
    # fixed like production classes, since the drift is in the test's
    # assumptions about signatures, not the implementation.
    test_files: tuple[str, ...] = ()
