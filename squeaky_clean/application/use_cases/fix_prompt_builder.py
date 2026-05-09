"""FixPromptBuilder: assembles the user prompt for one fixer LLM call."""

from squeaky_clean.application.dtos.fix_candidate import FixCandidate

_SYSTEM: str = (
    "You are a senior software engineer debugging a failing class. "
    "You receive the class SPEC, the CURRENT CODE, and TEST OUTPUT. "
    "Identify the defect and emit a corrected full file in a fenced "
    "code block. Emit ONLY the fenced block — no prose outside. "
    "THE SPEC IS AUTHORITATIVE: method return types, parameter types, "
    "and names in the emitted source MUST match the spec literally. "
    "If the test output suggests a different signature, the test is "
    "wrong — trust the spec. If the spec declares `Type[]` as a return "
    "type, the source MUST return `Type[]` (Java: array; TS: `Type[]`); "
    "never substitute `List<Type>`. Never rename methods to match tests."
)

_HEADER: str = (
    "The following class failed its tests. Diagnose the defect and "
    "emit a corrected full source file. Preserve the class name, "
    "file path, and the method signatures declared in the SPEC."
)


class FixPromptBuilder:
    """Builds system + user prompts for the fixer stage."""

    def system_prompt(self) -> str:
        """Return the shared fixer system prompt."""
        return _SYSTEM

    def user_prompt(self, candidate: FixCandidate) -> str:
        """Return the user prompt for fixing ``candidate``."""
        spec = candidate.class_spec
        fields = ", ".join(spec.fields) if spec.fields else ""
        methods = ", ".join(spec.methods) if spec.methods else ""
        return "\n".join([
            _HEADER, "",
            f"CLASS {spec.name}",
            f"PATTERN {spec.pattern}",
            f"FIELDS [{fields}]",
            f"METHODS [{methods}]",
            f"FILE_PATH {candidate.original.file_path}",
            "", "CURRENT CODE:",
            f"```\n{candidate.original.code}\n```",
            "", "TEST OUTPUT (failure excerpt):",
            f"```\n{candidate.failure_excerpt}\n```",
        ])
