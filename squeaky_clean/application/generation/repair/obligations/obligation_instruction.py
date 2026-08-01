"""obligation_instruction: repair-prompt text for undischarged obligations."""

from squeaky_clean.application.generation.testgen.test_obligation import TestObligation


def build_instruction(obs: list[TestObligation]) -> str:
    """Return the repair instruction covering every obligation in ``obs``."""
    lines = [
        "The generated test compiles but does NOT discharge these spec "
        "obligations. Add or strengthen a test for EACH so it exercises "
        "the behaviour and keeps a real assertion (never a trivial one):",
    ]
    for o in obs:
        if o.method == "<init>":
            lines.append(
                f"- from `{o.source}`: construct {o.target_class} with "
                f"input that VIOLATES \"{o.detail}\" and assert the "
                f"constructor raises")
        else:
            detail = o.detail or "the declared outcome"
            lines.append(
                f"- from `{o.source}`: call {o.method} on {o.target_class} "
                f"and assert it {o.kind.value} ({detail})")
    return "\n".join(lines)
