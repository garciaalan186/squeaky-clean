"""SecurityReviewFormatter: render context into a user prompt for SecurityArchitect."""

from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.domain.entities.class_spec import ClassSpec


class SecurityReviewFormatter:
    """Renders a SecurityReviewContext into the SecurityArchitect user prompt."""

    def format(self, ctx: SecurityReviewContext) -> str:
        """Return a compact plain-text description of module + problem."""
        module = ctx.module
        problem = ctx.problem
        lines: list[str] = [
            f"Module: {module.name}",
            f"Layer: {module.layer.value}",
            f"Description: {problem.description}",
            "AcceptanceCriteria:",
        ]
        for crit in problem.acceptance_criteria:
            lines.append(f"  - {crit}")
        lines.append("Classes:")
        for cls in module.classes:
            lines.append(self._format_class(cls))
        lines.append("")
        lines.append(
            "Review the above module for security concerns. "
            "Emit the SECURITY_REVIEW section exactly as specified."
        )
        return "\n".join(lines)

    def _format_class(self, cls: ClassSpec) -> str:
        fields = ", ".join(cls.fields) if cls.fields else ""
        methods = ", ".join(cls.methods) if cls.methods else ""
        return (
            f"  - {cls.name} [{cls.pattern}] "
            f"fields=[{fields}] methods=[{methods}]"
        )
